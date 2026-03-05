"""
SERVICIO DE USUARIOS
======================
Lógica de negocio para gestionar usuarios del sistema.
Equivale a UsuarioService.java en Spring Boot.

PATRÓN SERVICE:
  El router (controller) recibe la petición HTTP.
  El service contiene la lógica de negocio.
  El service usa SQLAlchemy (ORM) para acceder a la BD.

  Router → Service → SQLAlchemy ORM → Base de datos
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.services.auth_service import hash_password


def get_all(db: Session) -> list[Usuario]:
    """
    Obtiene todos los usuarios activos.
    Equivale a usuarioRepository.findAll() en Spring.
    """
    return db.query(Usuario).filter(Usuario.activo == True).all()


def get_by_id(db: Session, usuario_id: int) -> Usuario:
    """
    Busca un usuario por su ID.

    Raises:
        404 NOT_FOUND → Si no existe o está inactivo
    """
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id,
        Usuario.activo == True
    ).first()

    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    return usuario


def get_by_email(db: Session, email: str) -> Usuario | None:
    """Busca un usuario por email (retorna None si no existe)."""
    return db.query(Usuario).filter(Usuario.email == email).first()


def create(db: Session, usuario_data: UsuarioCreate) -> Usuario:
    """
    Crea un nuevo usuario.

    Pasos:
    1. Verificar que el email no esté en uso
    2. Hashear la contraseña
    3. Crear el objeto Usuario
    4. Guardar en la BD
    5. Retornar el usuario creado

    Raises:
        400 BAD_REQUEST → Si el email ya existe
    """
    # Verificar email único
    if get_by_email(db, usuario_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El email '{usuario_data.email}' ya está registrado"
        )

    # Crear el objeto de modelo (como new Usuario() en Java)
    nuevo_usuario = Usuario(
        email=usuario_data.email,
        nombre=usuario_data.nombre,
        hashed_password=hash_password(usuario_data.password),  # Hashear contraseña
        rol=usuario_data.rol,
        activo=True
    )

    # Añadir a la sesión y confirmar transacción
    db.add(nuevo_usuario)       # INSERT INTO usuarios VALUES (...)
    db.commit()                 # COMMIT (confirmar en BD)
    db.refresh(nuevo_usuario)   # Recargar desde BD (para obtener el ID generado)

    return nuevo_usuario


def update(db: Session, usuario_id: int, update_data: UsuarioUpdate) -> Usuario:
    """
    Actualiza un usuario existente.
    Solo actualiza los campos que se envíen (PATCH semántico).

    Raises:
        404 NOT_FOUND → Si el usuario no existe
    """
    usuario = get_by_id(db, usuario_id)

    # Obtener solo los campos que no son None
    # model_dump(exclude_none=True) → {"nombre": "Juan"} (sin campos vacíos)
    update_dict = update_data.model_dump(exclude_none=True)

    # Si se actualiza la contraseña, hashearla
    if "password" in update_dict:
        update_dict["hashed_password"] = hash_password(update_dict.pop("password"))

    # Actualizar solo los campos enviados
    for field, value in update_dict.items():
        setattr(usuario, field, value)

    db.commit()
    db.refresh(usuario)
    return usuario


def delete(db: Session, usuario_id: int) -> None:
    """
    Desactiva un usuario (soft delete).
    No se borra físicamente de la BD para mantener el historial.

    Equivale a soft delete en Spring (usuario.activo = false).

    Raises:
        404 NOT_FOUND → Si el usuario no existe
    """
    usuario = get_by_id(db, usuario_id)
    usuario.activo = False
    db.commit()
