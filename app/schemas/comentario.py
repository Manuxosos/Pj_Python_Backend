"""
SCHEMAS DE COMENTARIO
======================
DTOs para crear y responder con comentarios de tareas.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.usuario import UsuarioResumenResponse


class ComentarioCreate(BaseModel):
    """Datos para crear un comentario."""
    contenido: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        example="He terminado la implementación del JWT. Para review.",
        description="Texto del comentario"
    )


class ComentarioUpdate(BaseModel):
    """Actualizar contenido de un comentario."""
    contenido: str = Field(..., min_length=1, max_length=2000)


class ComentarioResponse(BaseModel):
    """Respuesta de un comentario."""
    id: int
    contenido: str
    created_at: datetime
    updated_at: datetime | None
    tarea_id: int
    autor: UsuarioResumenResponse

    model_config = {"from_attributes": True}
