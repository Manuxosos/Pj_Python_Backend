"""
SERVICIO DE TAREAS
===================
Lógica de negocio para gestionar tareas dentro de proyectos.
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.tarea import Tarea, EstadoTarea
from app.models.usuario import Usuario, RolUsuario
from app.schemas.tarea import TareaCreate, TareaUpdate, TareaEstadoUpdate
from app.services import proyecto_service


def get_by_proyecto(db: Session, proyecto_id: int) -> list[Tarea]:
    """Obtiene todas las tareas de un proyecto."""
    # Verificar que el proyecto existe
    proyecto_service.get_by_id(db, proyecto_id)

    return db.query(Tarea).filter(
        Tarea.proyecto_id == proyecto_id
    ).order_by(Tarea.created_at.desc()).all()


def get_by_id(db: Session, tarea_id: int) -> Tarea:
    """
    Busca una tarea por ID.

    Raises:
        404 NOT_FOUND → Si no existe
    """
    tarea = db.query(Tarea).filter(Tarea.id == tarea_id).first()
    if not tarea:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarea con ID {tarea_id} no encontrada"
        )
    return tarea


def get_mis_tareas(db: Session, usuario: Usuario) -> list[Tarea]:
    """Obtiene las tareas asignadas al usuario actual."""
    return db.query(Tarea).filter(
        Tarea.asignado_a_id == usuario.id,
        Tarea.estado != EstadoTarea.CANCELADA
    ).all()


def create(db: Session, tarea_data: TareaCreate, creador: Usuario) -> Tarea:
    """
    Crea una nueva tarea en un proyecto.

    Raises:
        404 → Si el proyecto no existe
        404 → Si el usuario asignado no existe
    """
    # Verificar que el proyecto existe
    proyecto_service.get_by_id(db, tarea_data.proyecto_id)

    nueva_tarea = Tarea(
        titulo=tarea_data.titulo,
        descripcion=tarea_data.descripcion,
        prioridad=tarea_data.prioridad,
        fecha_limite=tarea_data.fecha_limite,
        proyecto_id=tarea_data.proyecto_id,
        asignado_a_id=tarea_data.asignado_a_id,
        creado_por_id=creador.id,
        estado=EstadoTarea.PENDIENTE
    )

    db.add(nueva_tarea)
    db.commit()
    db.refresh(nueva_tarea)
    return nueva_tarea


def update(
    db: Session,
    tarea_id: int,
    update_data: TareaUpdate,
    usuario: Usuario
) -> Tarea:
    """
    Actualiza los datos de una tarea.
    Solo el creador, el asignado, o un ADMIN/MANAGER pueden actualizar.
    """
    tarea = get_by_id(db, tarea_id)
    _verificar_permiso_tarea(tarea, usuario)

    for field, value in update_data.model_dump(exclude_none=True).items():
        setattr(tarea, field, value)

    db.commit()
    db.refresh(tarea)
    return tarea


def cambiar_estado(
    db: Session,
    tarea_id: int,
    estado_data: TareaEstadoUpdate,
    usuario: Usuario
) -> Tarea:
    """
    Cambia el estado de una tarea.

    Si se marca como COMPLETADA, registra la fecha de completado.
    Si se reactiva, limpia la fecha de completado.

    CONCEPTO: Esta operación merece su propio endpoint porque
    en el mundo real cambiar el estado de una tarea es la
    operación más frecuente (drag & drop en tableros Kanban).
    """
    tarea = get_by_id(db, tarea_id)
    _verificar_permiso_tarea(tarea, usuario)

    tarea.estado = estado_data.estado

    # Registrar fecha de completado si aplica
    if estado_data.estado == EstadoTarea.COMPLETADA:
        tarea.fecha_completada = datetime.now(timezone.utc)
    else:
        tarea.fecha_completada = None

    db.commit()
    db.refresh(tarea)
    return tarea


def delete(db: Session, tarea_id: int, usuario: Usuario) -> None:
    """Elimina una tarea."""
    tarea = get_by_id(db, tarea_id)
    _verificar_permiso_tarea(tarea, usuario)

    db.delete(tarea)
    db.commit()


def _verificar_permiso_tarea(tarea: Tarea, usuario: Usuario) -> None:
    """
    Verifica que el usuario puede modificar la tarea.
    Puede si es: el creador, el asignado, o un ADMIN/MANAGER.

    Función interna (prefijo _) = privada a este módulo.
    Equivale a un método privado en Java.
    """
    puede = (
        tarea.creado_por_id == usuario.id
        or tarea.asignado_a_id == usuario.id
        or usuario.rol in [RolUsuario.ADMIN, RolUsuario.MANAGER]
    )
    if not puede:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para modificar esta tarea"
        )
