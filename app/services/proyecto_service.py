"""
SERVICIO DE PROYECTOS
=======================
Lógica de negocio para gestionar proyectos.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.proyecto import Proyecto
from app.models.usuario import Usuario, RolUsuario
from app.schemas.proyecto import ProyectoCreate, ProyectoUpdate


def get_all(db: Session, usuario: Usuario) -> list[Proyecto]:
    """
    Obtiene proyectos según el rol del usuario:
    - ADMIN: todos los proyectos
    - MANAGER/DESARROLLADOR: solo los proyectos donde es owner
    """
    if usuario.rol == RolUsuario.ADMIN:
        return db.query(Proyecto).all()
    return db.query(Proyecto).filter(Proyecto.owner_id == usuario.id).all()


def get_by_id(db: Session, proyecto_id: int) -> Proyecto:
    """
    Busca un proyecto por ID.

    Raises:
        404 NOT_FOUND → Si no existe
    """
    proyecto = db.query(Proyecto).filter(Proyecto.id == proyecto_id).first()
    if not proyecto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proyecto con ID {proyecto_id} no encontrado"
        )
    return proyecto


def create(db: Session, proyecto_data: ProyectoCreate, owner: Usuario) -> Proyecto:
    """
    Crea un nuevo proyecto.
    El owner es el usuario que hace la petición (del JWT).
    """
    nuevo_proyecto = Proyecto(
        nombre=proyecto_data.nombre,
        descripcion=proyecto_data.descripcion,
        fecha_inicio=proyecto_data.fecha_inicio,
        fecha_fin_estimada=proyecto_data.fecha_fin_estimada,
        owner_id=owner.id
    )

    db.add(nuevo_proyecto)
    db.commit()
    db.refresh(nuevo_proyecto)
    return nuevo_proyecto


def update(
    db: Session,
    proyecto_id: int,
    update_data: ProyectoUpdate,
    usuario: Usuario
) -> Proyecto:
    """
    Actualiza un proyecto.
    Solo el owner o un ADMIN pueden actualizar.

    Raises:
        403 FORBIDDEN → Si no es el owner ni ADMIN
    """
    proyecto = get_by_id(db, proyecto_id)

    # Verificar permisos
    if proyecto.owner_id != usuario.id and usuario.rol != RolUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el creador del proyecto o un administrador puede modificarlo"
        )

    # Actualizar campos enviados
    for field, value in update_data.model_dump(exclude_none=True).items():
        setattr(proyecto, field, value)

    db.commit()
    db.refresh(proyecto)
    return proyecto


def delete(db: Session, proyecto_id: int, usuario: Usuario) -> None:
    """
    Elimina un proyecto y todas sus tareas (por el cascade).
    Solo el owner o ADMIN pueden eliminar.

    Raises:
        403 FORBIDDEN → Si no tiene permisos
    """
    proyecto = get_by_id(db, proyecto_id)

    if proyecto.owner_id != usuario.id and usuario.rol != RolUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar este proyecto"
        )

    db.delete(proyecto)
    db.commit()
