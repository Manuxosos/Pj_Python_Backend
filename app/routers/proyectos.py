"""
ROUTER DE PROYECTOS
====================
CRUD de proyectos con filtrado por rol.

DISEÑO REST:
  GET    /api/proyectos/         → Listar proyectos
  POST   /api/proyectos/         → Crear proyecto
  GET    /api/proyectos/{id}     → Ver proyecto
  PUT    /api/proyectos/{id}     → Actualizar proyecto
  DELETE /api/proyectos/{id}     → Eliminar proyecto
  GET    /api/proyectos/{id}/tareas → Tareas del proyecto
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.usuario import Usuario
from app.schemas.proyecto import ProyectoCreate, ProyectoUpdate, ProyectoResponse
from app.schemas.tarea import TareaResponse
from app.security.dependencies import get_usuario_actual, require_manager_or_admin
from app.services import proyecto_service, tarea_service

router = APIRouter(
    prefix="/api/proyectos",
    tags=["📁 Proyectos"],
)


@router.get(
    "/",
    response_model=list[ProyectoResponse],
    summary="Listar proyectos"
)
def listar_proyectos(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    """
    ADMIN ve todos los proyectos.
    MANAGER/DESARROLLADOR ven solo sus proyectos.
    """
    proyectos = proyecto_service.get_all(db, usuario_actual)

    # Construir respuesta con campo calculado total_tareas
    resultado = []
    for p in proyectos:
        proyecto_dict = {
            "id": p.id,
            "nombre": p.nombre,
            "descripcion": p.descripcion,
            "estado": p.estado,
            "fecha_inicio": p.fecha_inicio,
            "fecha_fin_estimada": p.fecha_fin_estimada,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
            "owner": p.owner,
            "total_tareas": len(p.tareas)  # Campo calculado
        }
        resultado.append(ProyectoResponse(**proyecto_dict))

    return resultado


@router.post(
    "/",
    response_model=ProyectoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear proyecto"
)
def crear_proyecto(
    proyecto_data: ProyectoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(require_manager_or_admin)
):
    """Solo MANAGER o ADMIN pueden crear proyectos."""
    proyecto = proyecto_service.create(db, proyecto_data, usuario_actual)
    return ProyectoResponse(
        **{
            "id": proyecto.id,
            "nombre": proyecto.nombre,
            "descripcion": proyecto.descripcion,
            "estado": proyecto.estado,
            "fecha_inicio": proyecto.fecha_inicio,
            "fecha_fin_estimada": proyecto.fecha_fin_estimada,
            "created_at": proyecto.created_at,
            "updated_at": proyecto.updated_at,
            "owner": proyecto.owner,
            "total_tareas": 0
        }
    )


@router.get(
    "/{proyecto_id}",
    response_model=ProyectoResponse,
    summary="Ver proyecto"
)
def ver_proyecto(
    proyecto_id: int,
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(get_usuario_actual)
):
    proyecto = proyecto_service.get_by_id(db, proyecto_id)
    return ProyectoResponse(
        **{
            "id": proyecto.id,
            "nombre": proyecto.nombre,
            "descripcion": proyecto.descripcion,
            "estado": proyecto.estado,
            "fecha_inicio": proyecto.fecha_inicio,
            "fecha_fin_estimada": proyecto.fecha_fin_estimada,
            "created_at": proyecto.created_at,
            "updated_at": proyecto.updated_at,
            "owner": proyecto.owner,
            "total_tareas": len(proyecto.tareas)
        }
    )


@router.put(
    "/{proyecto_id}",
    response_model=ProyectoResponse,
    summary="Actualizar proyecto"
)
def actualizar_proyecto(
    proyecto_id: int,
    update_data: ProyectoUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    proyecto = proyecto_service.update(db, proyecto_id, update_data, usuario_actual)
    return ProyectoResponse(
        **{
            "id": proyecto.id,
            "nombre": proyecto.nombre,
            "descripcion": proyecto.descripcion,
            "estado": proyecto.estado,
            "fecha_inicio": proyecto.fecha_inicio,
            "fecha_fin_estimada": proyecto.fecha_fin_estimada,
            "created_at": proyecto.created_at,
            "updated_at": proyecto.updated_at,
            "owner": proyecto.owner,
            "total_tareas": len(proyecto.tareas)
        }
    )


@router.delete(
    "/{proyecto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar proyecto"
)
def eliminar_proyecto(
    proyecto_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    proyecto_service.delete(db, proyecto_id, usuario_actual)


@router.get(
    "/{proyecto_id}/tareas",
    response_model=list[TareaResponse],
    summary="Tareas del proyecto"
)
def tareas_del_proyecto(
    proyecto_id: int,
    db: Session = Depends(get_db),
    _usuario: Usuario = Depends(get_usuario_actual)
):
    """
    Obtiene todas las tareas de un proyecto específico.
    Este es un endpoint "nested resource" (recurso anidado),
    patrón común en APIs REST: /proyectos/{id}/tareas
    """
    tareas = tarea_service.get_by_proyecto(db, proyecto_id)
    resultado = []
    for t in tareas:
        resultado.append(TareaResponse(
            **{
                "id": t.id,
                "titulo": t.titulo,
                "descripcion": t.descripcion,
                "estado": t.estado,
                "prioridad": t.prioridad,
                "fecha_limite": t.fecha_limite,
                "fecha_completada": t.fecha_completada,
                "created_at": t.created_at,
                "proyecto_id": t.proyecto_id,
                "asignado_a": t.asignado_a,
                "creado_por": t.creado_por,
                "total_comentarios": len(t.comentarios)
            }
        ))
    return resultado
