"""
SCHEMAS DE TAREA
=================
DTOs para el CRUD de tareas y actualización de estado.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from app.models.tarea import EstadoTarea, PrioridadTarea
from app.schemas.usuario import UsuarioResumenResponse


class TareaCreate(BaseModel):
    """Datos para crear una nueva tarea."""
    titulo: str = Field(
        ...,
        min_length=3,
        max_length=300,
        example="Implementar login con JWT",
        description="Título claro de la tarea"
    )
    descripcion: str | None = Field(
        None,
        example="Usar python-jose para generar y verificar tokens JWT"
    )
    prioridad: PrioridadTarea = Field(
        default=PrioridadTarea.MEDIA,
        description="Nivel de urgencia"
    )
    fecha_limite: datetime | None = Field(None, example="2024-03-01T00:00:00")
    proyecto_id: int = Field(..., description="ID del proyecto al que pertenece")
    asignado_a_id: int | None = Field(None, description="ID del usuario asignado")


class TareaUpdate(BaseModel):
    """Datos para actualizar una tarea (todos opcionales)."""
    titulo: str | None = Field(None, min_length=3, max_length=300)
    descripcion: str | None = None
    prioridad: PrioridadTarea | None = None
    fecha_limite: datetime | None = None
    asignado_a_id: int | None = None


class TareaEstadoUpdate(BaseModel):
    """
    Schema especial para cambiar el estado de una tarea.
    En la API real, cambiar el estado es una operación frecuente
    y merece su propio endpoint (RESTful best practice).
    """
    estado: EstadoTarea = Field(..., description="Nuevo estado de la tarea")


class TareaResponse(BaseModel):
    """Respuesta completa de una tarea."""
    id: int
    titulo: str
    descripcion: str | None
    estado: EstadoTarea
    prioridad: PrioridadTarea
    fecha_limite: datetime | None
    fecha_completada: datetime | None
    created_at: datetime
    proyecto_id: int
    asignado_a: UsuarioResumenResponse | None
    creado_por: UsuarioResumenResponse
    total_comentarios: int = 0

    model_config = {"from_attributes": True}


class TareaResumenResponse(BaseModel):
    """Versión reducida de tarea."""
    id: int
    titulo: str
    estado: EstadoTarea
    prioridad: PrioridadTarea

    model_config = {"from_attributes": True}
