"""
ROUTER DE TAREAS
==================
CRUD de tareas con endpoint especial para cambiar estado.

ENDPOINTS ESPECIALES:
  PATCH /api/tareas/{id}/estado → Cambiar estado (Pendiente→En progreso→Completada)
  GET   /api/tareas/mis-tareas  → Tareas asignadas al usuario actual

¿Por qué PATCH y no PUT para el estado?
  PUT    → actualización COMPLETA del recurso
  PATCH  → actualización PARCIAL (solo algunos campos)

  Cambiar solo el estado es una actualización parcial → PATCH
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.usuario import Usuario
from app.schemas.tarea import TareaCreate, TareaUpdate, TareaEstadoUpdate, TareaResponse
from app.security.dependencies import get_usuario_actual
from app.services import tarea_service

router = APIRouter(
    prefix="/api/tareas",
    tags=["✅ Tareas"],
)


def _tarea_to_response(tarea) -> TareaResponse:
    """Helper para convertir modelo a schema de respuesta."""
    return TareaResponse(
        **{
            "id": tarea.id,
            "titulo": tarea.titulo,
            "descripcion": tarea.descripcion,
            "estado": tarea.estado,
            "prioridad": tarea.prioridad,
            "fecha_limite": tarea.fecha_limite,
            "fecha_completada": tarea.fecha_completada,
            "created_at": tarea.created_at,
            "proyecto_id": tarea.proyecto_id,
            "asignado_a": tarea.asignado_a,
            "creado_por": tarea.creado_por,
            "total_comentarios": len(tarea.comentarios)
        }
    )


@router.get(
    "/mis-tareas",
    response_model=list[TareaResponse],
    summary="Mis tareas asignadas"
)
def mis_tareas(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    """
    Devuelve las tareas asignadas al usuario que hace la petición.
    IMPORTANTE: Este endpoint debe ir ANTES de /{tarea_id}
    o FastAPI lo interpretaría como un ID.
    """
    tareas = tarea_service.get_mis_tareas(db, usuario_actual)
    return [_tarea_to_response(t) for t in tareas]


@router.post(
    "/",
    response_model=TareaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear tarea"
)
def crear_tarea(
    tarea_data: TareaCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    tarea = tarea_service.create(db, tarea_data, usuario_actual)
    return _tarea_to_response(tarea)


@router.get(
    "/{tarea_id}",
    response_model=TareaResponse,
    summary="Ver tarea"
)
def ver_tarea(
    tarea_id: int,
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(get_usuario_actual)
):
    tarea = tarea_service.get_by_id(db, tarea_id)
    return _tarea_to_response(tarea)


@router.put(
    "/{tarea_id}",
    response_model=TareaResponse,
    summary="Actualizar tarea"
)
def actualizar_tarea(
    tarea_id: int,
    update_data: TareaUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    tarea = tarea_service.update(db, tarea_id, update_data, usuario_actual)
    return _tarea_to_response(tarea)


@router.patch(
    "/{tarea_id}/estado",
    response_model=TareaResponse,
    summary="Cambiar estado de tarea",
    description="""
    Cambia el estado de la tarea.

    Flujo típico:
    PENDIENTE → EN_PROGRESO → EN_REVISION → COMPLETADA

    O puede cancelarse desde cualquier estado:
    * → CANCELADA
    """
)
def cambiar_estado(
    tarea_id: int,
    estado_data: TareaEstadoUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    """
    Endpoint PATCH: solo actualiza el estado.
    Este patrón (endpoint dedicado para acciones) es muy común en APIs REST.
    """
    tarea = tarea_service.cambiar_estado(db, tarea_id, estado_data, usuario_actual)
    return _tarea_to_response(tarea)


@router.delete(
    "/{tarea_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar tarea"
)
def eliminar_tarea(
    tarea_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    tarea_service.delete(db, tarea_id, usuario_actual)
