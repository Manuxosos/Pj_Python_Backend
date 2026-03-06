"""
SERVICIO DE USUARIOS
======================
Gestiona el CRUD de usuarios y el registro público.
Router → Service → SQLAlchemy ORM → Base de datos
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.usuario import Usuario, RolUsuario
from app.models.carrito import Carrito
from app.schemas.usuario import UsuarioRegistro, UsuarioCreate, UsuarioUpdate
from app.services.auth_service import hash_password


def get_all(db: Session) -> list[Usuario]:
    """Lista todos los usuarios activos."""
    return db.query(Usuario).filter(Usuario.activo == True).all()


def get_by_id(db: Session, usuario_id: int) -> Usuario:
    """Busca un usuario por ID. Lanza 404 si no existe."""
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id, Usuario.activo == True
    ).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    return usuario


def get_by_email(db: Session, email: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.email == email).first()


def registrar(db: Session, datos: UsuarioRegistro) -> Usuario:
    """
    Registro público: crea un nuevo CLIENTE.
    También crea automáticamente un carrito vacío para el usuario.

    Este endpoint es PÚBLICO (sin autenticación).
    Es el equivalente al botón "Crear cuenta" del frontend.
    """
    if get_by_email(db, datos.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El email '{datos.email}' ya está registrado"
        )

    nuevo_usuario = Usuario(
        email=datos.email,
        nombre=datos.nombre,
        apellido=datos.apellido,
        hashed_password=hash_password(datos.password),
        rol=RolUsuario.CLIENTE,  # Registro público → siempre CLIENTE
        activo=True
    )
    db.add(nuevo_usuario)
    db.flush()  # Necesitamos el ID antes del commit para el carrito

    # Crear carrito vacío automáticamente al registrarse
    carrito = Carrito(usuario_id=nuevo_usuario.id)
    db.add(carrito)

    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


def create(db: Session, datos: UsuarioCreate) -> Usuario:
    """
    Creación por admin: puede asignar cualquier rol.
    También crea el carrito automáticamente.
    """
    if get_by_email(db, datos.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El email '{datos.email}' ya está registrado"
        )

    nuevo_usuario = Usuario(
        email=datos.email,
        nombre=datos.nombre,
        apellido=datos.apellido,
        hashed_password=hash_password(datos.password),
        rol=datos.rol,
        activo=True
    )
    db.add(nuevo_usuario)
    db.flush()

    carrito = Carrito(usuario_id=nuevo_usuario.id)
    db.add(carrito)

    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


def update(db: Session, usuario_id: int, datos: UsuarioUpdate) -> Usuario:
    """Actualiza perfil. Solo campos enviados (exclude_none=True)."""
    usuario = get_by_id(db, usuario_id)
    update_dict = datos.model_dump(exclude_none=True)

    if "password" in update_dict:
        update_dict["hashed_password"] = hash_password(update_dict.pop("password"))

    for field, value in update_dict.items():
        setattr(usuario, field, value)

    db.commit()
    db.refresh(usuario)
    return usuario


def delete(db: Session, usuario_id: int) -> None:
    """Soft delete: desactiva el usuario sin borrar su historial de pedidos."""
    usuario = get_by_id(db, usuario_id)
    usuario.activo = False
    db.commit()
