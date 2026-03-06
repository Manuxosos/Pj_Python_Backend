"""
SCHEMAS DE PRODUCTO
====================

CONCEPTO IMPORTANTE - Endpoints públicos vs privados:
  GET /api/productos/        → PÚBLICO (sin login)
  POST /api/productos/       → PRIVADO (solo ADMIN)

  El catálogo de productos es público porque cualquier visitante
  de la tienda debe poder verlo sin estar registrado.
  Esto es fundamental para el frontend: las páginas de producto
  tienen que cargarse sin autenticación (SEO, accesibilidad).

FILTROS DE BÚSQUEDA:
  El endpoint de listar productos acepta query parameters:
  /api/productos/?categoria_id=1&busqueda=laptop&min_precio=100&max_precio=2000
"""

from datetime import datetime
from pydantic import BaseModel, Field


class ProductoCreate(BaseModel):
    nombre: str = Field(
        ..., min_length=3, max_length=300,
        example="MacBook Pro M3 14 pulgadas"
    )
    descripcion: str | None = Field(
        None,
        example="El portátil más potente de Apple con chip M3 y 18h de batería"
    )
    precio: float = Field(..., gt=0, example=2199.99, description="Precio en euros")
    precio_descuento: float | None = Field(
        None, gt=0, example=1999.99,
        description="Precio de oferta (debe ser menor al precio original)"
    )
    stock: int = Field(default=0, ge=0, example=50, description="Unidades disponibles")
    imagen_url: str | None = Field(None, example="https://ejemplo.com/macbook.jpg")
    categoria_id: int = Field(..., description="ID de la categoría")
    destacado: bool = Field(default=False, description="Mostrar en el home de la tienda")


class ProductoUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=3, max_length=300)
    descripcion: str | None = None
    precio: float | None = Field(None, gt=0)
    precio_descuento: float | None = None
    stock: int | None = Field(None, ge=0)
    imagen_url: str | None = None
    categoria_id: int | None = None
    activo: bool | None = None
    destacado: bool | None = None


class ProductoResponse(BaseModel):
    """
    Lo que el frontend recibe al pedir un producto.
    Incluye campos calculados como precio_final y tiene_descuento.
    """
    id: int
    nombre: str
    descripcion: str | None
    precio: float
    precio_descuento: float | None
    precio_final: float          # Campo calculado: precio o precio_descuento
    tiene_descuento: bool        # True si hay oferta activa
    porcentaje_descuento: float  # Ej: 15.0 (= 15% de descuento)
    stock: int
    disponible: bool             # True si stock > 0
    imagen_url: str | None
    destacado: bool
    categoria_id: int
    categoria_nombre: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductoResumenResponse(BaseModel):
    """Versión card del producto (para listados, carrito, pedidos)."""
    id: int
    nombre: str
    precio_final: float
    tiene_descuento: bool
    imagen_url: str | None
    stock: int
    disponible: bool

    model_config = {"from_attributes": True}
