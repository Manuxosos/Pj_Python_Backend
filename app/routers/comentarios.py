"""
ROUTER DE COMENTARIOS
=======================
CRUD de comentarios dentro de tareas.
Los comentarios están anidados bajo las tareas:
  /api/tareas/{tarea_id}/comentarios
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.usuario import Usuario
from app.schemas.comentario import ComentarioCreate, ComentarioUpdate, ComentarioResponse
from app.security.dependencies import get_usuario_actual
from app.services import comentario_service

router = APIRouter(
    prefix="/api/tareas/{tarea_id}/comentarios",
    tags=["💬 Comentarios"],
)


@router.get(
    "/",
    response_model=list[ComentarioResponse],
    summary="Ver comentarios de una tarea"
)
def listar_comentarios(
    tarea_id: int,
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(get_usuario_actual)
):
    return comentario_service.get_by_tarea(db, tarea_id)


@router.post(
    "/",
    response_model=ComentarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Añadir comentario"
)
def crear_comentario(
    tarea_id: int,
    comentario_data: ComentarioCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    return comentario_service.create(db, tarea_id, comentario_data, usuario_actual)


@router.put(
    "/{comentario_id}",
    response_model=ComentarioResponse,
    summary="Editar comentario"
)
def editar_comentario(
    tarea_id: int,
    comentario_id: int,
    update_data: ComentarioUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    return comentario_service.update(db, comentario_id, update_data, usuario_actual)


@router.delete(
    "/{comentario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar comentario"
)
def eliminar_comentario(
    tarea_id: int,
    comentario_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    comentario_service.delete(db, comentario_id, usuario_actual)
