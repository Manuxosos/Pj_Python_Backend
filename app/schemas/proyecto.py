"""
SCHEMAS DE PROYECTO
====================
DTOs para crear, actualizar y responder con datos de proyectos.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from app.models.proyecto import EstadoProyecto
from app.schemas.usuario import UsuarioResumenResponse


class ProyectoCreate(BaseModel):
    """Datos para crear un nuevo proyecto."""
    nombre: str = Field(
        ...,
        min_length=3,
        max_length=200,
        example="Portal de Clientes",
        description="Nombre descriptivo del proyecto"
    )
    descripcion: str | None = Field(
        None,
        example="Sistema web para gestión de clientes B2B"
    )
    fecha_inicio: datetime | None = Field(None, example="2024-01-15T00:00:00")
    fecha_fin_estimada: datetime | None = Field(None, example="2024-06-30T00:00:00")


class ProyectoUpdate(BaseModel):
    """Datos para actualizar un proyecto (todos opcionales)."""
    nombre: str | None = Field(None, min_length=3, max_length=200)
    descripcion: str | None = None
    estado: EstadoProyecto | None = None
    fecha_inicio: datetime | None = None
    fecha_fin_estimada: datetime | None = None


class ProyectoResponse(BaseModel):
    """Respuesta completa de un proyecto."""
    id: int
    nombre: str
    descripcion: str | None
    estado: EstadoProyecto
    fecha_inicio: datetime | None
    fecha_fin_estimada: datetime | None
    created_at: datetime
    updated_at: datetime | None
    owner: UsuarioResumenResponse
    total_tareas: int = 0  # Campo calculado

    model_config = {"from_attributes": True}


class ProyectoResumenResponse(BaseModel):
    """Versión reducida del proyecto (para listar)."""
    id: int
    nombre: str
    estado: EstadoProyecto
    total_tareas: int = 0

    model_config = {"from_attributes": True}
