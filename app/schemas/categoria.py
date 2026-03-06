"""
SCHEMAS DE CATEGORÍA
"""

from datetime import datetime
from pydantic import BaseModel, Field


class CategoriaCreate(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, example="Electrónica")
    descripcion: str | None = Field(None, example="Dispositivos electrónicos y tecnología")
    icono: str | None = Field(None, example="laptop")


class CategoriaUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=2, max_length=100)
    descripcion: str | None = None
    icono: str | None = None
    activo: bool | None = None


class CategoriaResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str | None
    icono: str | None
    activo: bool
    total_productos: int = 0

    model_config = {"from_attributes": True}
