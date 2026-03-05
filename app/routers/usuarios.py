"""
ROUTER DE USUARIOS
====================
CRUD completo de usuarios.
Solo ADMIN puede ver todos los usuarios y crear nuevos.
Un usuario puede ver y actualizar su propio perfil.

CÓDIGOS HTTP que usamos:
  200 OK         → GET exitoso
  201 CREATED    → POST exitoso (recurso creado)
  204 NO_CONTENT → DELETE exitoso (sin body de respuesta)
  400 BAD_REQUEST    → Error de validación o negocio
  401 UNAUTHORIZED   → No autenticado
  403 FORBIDDEN      → Sin permisos
  404 NOT_FOUND      → Recurso no encontrado
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from app.security.dependencies import get_usuario_actual, require_admin
from app.services import usuario_service

router = APIRouter(
    prefix="/api/usuarios",
    tags=["👥 Usuarios"],
)


@router.get(
    "/",
    response_model=list[UsuarioResponse],
    summary="Listar usuarios",
    description="Solo administradores pueden ver todos los usuarios."
)
def listar_usuarios(
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_admin)  # _ indica que no usamos la variable
):
    return usuario_service.get_all(db)


@router.post(
    "/",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario",
    description="Solo ADMIN puede crear usuarios."
)
def crear_usuario(
    usuario_data: UsuarioCreate,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_admin)
):
    return usuario_service.create(db, usuario_data)


@router.get(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Ver un usuario",
    description="ADMIN puede ver cualquier usuario. Un usuario puede verse a sí mismo."
)
def ver_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    from app.models.usuario import RolUsuario
    # Un usuario solo puede ver su propio perfil (a menos que sea ADMIN)
    if usuario_actual.rol != RolUsuario.ADMIN and usuario_actual.id != usuario_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Sin permisos para ver este usuario")

    return usuario_service.get_by_id(db, usuario_id)


@router.put(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    summary="Actualizar usuario",
    description="Un usuario puede actualizar su propio perfil. ADMIN puede actualizar cualquiera."
)
def actualizar_usuario(
    usuario_id: int,
    update_data: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    from app.models.usuario import RolUsuario
    if usuario_actual.rol != RolUsuario.ADMIN and usuario_actual.id != usuario_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Sin permisos para modificar este usuario")

    return usuario_service.update(db, usuario_id, update_data)


@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desactivar usuario",
    description="Solo ADMIN. Realiza un soft-delete (no borra físicamente)."
)
def desactivar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_admin)
):
    usuario_service.delete(db, usuario_id)
    # 204 no devuelve body → return None
