"""
SCHEMAS DE CARRITO
===================
El carrito es la parte más interactiva del e-commerce.
El frontend llama a estos endpoints con cada acción del usuario.

OPERACIONES DEL CARRITO (desde el frontend):
  - Ver carrito:          GET  /api/carrito/
  - Añadir producto:      POST /api/carrito/items
  - Cambiar cantidad:     PUT  /api/carrito/items/{producto_id}
  - Quitar producto:      DELETE /api/carrito/items/{producto_id}
  - Vaciar carrito:       DELETE /api/carrito/

CONCEPTOS FRONTEND:
  Cuando el usuario hace click en "Añadir al carrito":
    1. Frontend llama: POST /api/carrito/items {"producto_id": 5, "cantidad": 1}
    2. Backend verifica stock y añade al carrito en BD
    3. Backend responde con el carrito actualizado
    4. Frontend actualiza el contador del carrito en el header
"""

from pydantic import BaseModel, Field
from app.schemas.producto import ProductoResumenResponse


class AnadirItemRequest(BaseModel):
    """Lo que envía el frontend al hacer click en 'Añadir al carrito'."""
    producto_id: int = Field(..., description="ID del producto a añadir")
    cantidad: int = Field(default=1, ge=1, le=99, description="Unidades a añadir")


class ActualizarCantidadRequest(BaseModel):
    """Cambiar la cantidad de un producto en el carrito."""
    cantidad: int = Field(..., ge=1, le=99, description="Nueva cantidad")


class CarritoItemResponse(BaseModel):
    """Un item dentro del carrito con info del producto."""
    id: int
    producto: ProductoResumenResponse
    cantidad: int
    subtotal: float   # precio_final × cantidad

    model_config = {"from_attributes": True}


class CarritoResponse(BaseModel):
    """El carrito completo con todos sus items y el total."""
    id: int
    items: list[CarritoItemResponse]
    total: float         # Suma de todos los subtotales
    total_items: int     # Total de unidades (no tipos de producto)

    model_config = {"from_attributes": True}
