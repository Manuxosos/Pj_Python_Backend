"""
SERVICIO DE COMENTARIOS
========================
Gestiona los comentarios en las tareas.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.comentario import Comentario
from app.models.usuario import Usuario, RolUsuario
from app.schemas.comentario import ComentarioCreate, ComentarioUpdate
from app.services import tarea_service


def get_by_tarea(db: Session, tarea_id: int) -> list[Comentario]:
    """Obtiene todos los comentarios de una tarea."""
    tarea_service.get_by_id(db, tarea_id)  # Verificar que la tarea existe
    return db.query(Comentario).filter(
        Comentario.tarea_id == tarea_id
    ).order_by(Comentario.created_at).all()


def create(
    db: Session,
    tarea_id: int,
    comentario_data: ComentarioCreate,
    autor: Usuario
) -> Comentario:
    """Crea un comentario en una tarea."""
    tarea_service.get_by_id(db, tarea_id)  # Verificar que la tarea existe

    comentario = Comentario(
        contenido=comentario_data.contenido,
        tarea_id=tarea_id,
        autor_id=autor.id
    )

    db.add(comentario)
    db.commit()
    db.refresh(comentario)
    return comentario


def update(
    db: Session,
    comentario_id: int,
    update_data: ComentarioUpdate,
    usuario: Usuario
) -> Comentario:
    """
    Actualiza un comentario.
    Solo el autor o un ADMIN puede editar.
    """
    comentario = _get_by_id(db, comentario_id)

    if comentario.autor_id != usuario.id and usuario.rol != RolUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el autor puede editar su comentario"
        )

    comentario.contenido = update_data.contenido
    db.commit()
    db.refresh(comentario)
    return comentario


def delete(db: Session, comentario_id: int, usuario: Usuario) -> None:
    """Elimina un comentario. Solo el autor o ADMIN pueden borrarlo."""
    comentario = _get_by_id(db, comentario_id)

    if comentario.autor_id != usuario.id and usuario.rol != RolUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el autor puede eliminar su comentario"
        )

    db.delete(comentario)
    db.commit()


def _get_by_id(db: Session, comentario_id: int) -> Comentario:
    """Busca un comentario por ID."""
    comentario = db.query(Comentario).filter(Comentario.id == comentario_id).first()
    if not comentario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comentario con ID {comentario_id} no encontrado"
        )
    return comentario
