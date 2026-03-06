"""
ROUTER DE USUARIOS
====================
Gestión de usuarios por el ADMIN.
El registro público está en /api/auth/registro.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.usuario import Usuario, RolUsuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioResponse
from app.security.dependencies import get_usuario_actual, require_admin
from app.services import usuario_service

router = APIRouter(prefix="/api/usuarios", tags=["👥 Usuarios (Admin)"])


@router.get("/", response_model=list[UsuarioResponse], summary="Listar todos los usuarios")
def listar_usuarios(db: Session = Depends(get_db), _admin: Usuario = Depends(require_admin)):
    """Solo ADMIN puede ver la lista completa de clientes."""
    return usuario_service.get_all(db)


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED,
             summary="Crear usuario (admin)")
def crear_usuario(datos: UsuarioCreate, db: Session = Depends(get_db),
                  _admin: Usuario = Depends(require_admin)):
    """El ADMIN puede crear usuarios con cualquier rol."""
    return usuario_service.create(db, datos)


@router.get("/{usuario_id}", response_model=UsuarioResponse, summary="Ver usuario")
def ver_usuario(usuario_id: int, db: Session = Depends(get_db),
                usuario_actual: Usuario = Depends(get_usuario_actual)):
    """ADMIN ve cualquier usuario. Un cliente solo puede verse a sí mismo."""
    if usuario_actual.rol != RolUsuario.ADMIN and usuario_actual.id != usuario_id:
        raise HTTPException(status_code=403, detail="Solo puedes ver tu propio perfil")
    return usuario_service.get_by_id(db, usuario_id)


@router.put("/{usuario_id}", response_model=UsuarioResponse, summary="Actualizar perfil")
def actualizar_usuario(usuario_id: int, datos: UsuarioUpdate,
                       db: Session = Depends(get_db),
                       usuario_actual: Usuario = Depends(get_usuario_actual)):
    """Un usuario actualiza su propio perfil. ADMIN puede actualizar cualquiera."""
    if usuario_actual.rol != RolUsuario.ADMIN and usuario_actual.id != usuario_id:
        raise HTTPException(status_code=403, detail="Solo puedes modificar tu propio perfil")
    return usuario_service.update(db, usuario_id, datos)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Desactivar usuario")
def desactivar_usuario(usuario_id: int, db: Session = Depends(get_db),
                       _admin: Usuario = Depends(require_admin)):
    """Soft delete. El historial de pedidos del usuario se conserva."""
    usuario_service.delete(db, usuario_id)
