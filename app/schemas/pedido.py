"""
SCHEMAS DE PEDIDO
==================
El pedido es la operación más crítica del e-commerce.

FLUJO DE CHECKOUT (desde el frontend):
  1. Usuario ve su carrito
  2. Introduce dirección de envío
  3. Pulsa "Confirmar pedido"
  4. Frontend llama: POST /api/pedidos/ {"direccion_envio": "...", "notas": "..."}
  5. Backend:
     a. Verifica que el carrito no está vacío
     b. Verifica stock de cada producto
     c. Crea el pedido con los items del carrito
     d. Descuenta el stock de cada producto
     e. Vacía el carrito
     f. Devuelve el pedido creado
  6. Frontend muestra página de "¡Pedido confirmado! #1234"

ESTE FLUJO ES TRANSACCIONAL:
  Si cualquier paso falla (ej: un producto sin stock),
  TODO se revierte. O se hace todo, o no se hace nada.
  Esto se llama "atomicidad" y es una propiedad ACID de las BD.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from app.models.pedido import EstadoPedido
from app.schemas.usuario import UsuarioResumenResponse


class CrearPedidoRequest(BaseModel):
    """
    Lo que el cliente envía al hacer checkout.
    El contenido del pedido se toma del carrito del usuario.
    """
    direccion_envio: str = Field(
        ...,
        min_length=10,
        example="Calle Mayor 15, 3ºB, 28001 Madrid, España"
    )
    notas: str | None = Field(
        None,
        example="Dejar en portería si no hay nadie en casa"
    )


class ActualizarEstadoPedidoRequest(BaseModel):
    """Solo el ADMIN puede cambiar el estado de un pedido."""
    estado: EstadoPedido = Field(..., description="Nuevo estado del pedido")


class PedidoItemResponse(BaseModel):
    id: int
    producto_id: int
    nombre_producto: str    # Snapshot del nombre en el momento de compra
    cantidad: int
    precio_unitario: float  # Snapshot del precio en el momento de compra
    subtotal: float

    model_config = {"from_attributes": True}


class PedidoResponse(BaseModel):
    id: int
    estado: EstadoPedido
    total: float
    direccion_envio: str
    notas: str | None
    created_at: datetime
    updated_at: datetime | None
    items: list[PedidoItemResponse]
    usuario: UsuarioResumenResponse

    model_config = {"from_attributes": True}


class PedidoResumenResponse(BaseModel):
    """Para listar pedidos (sin el detalle de items)."""
    id: int
    estado: EstadoPedido
    total: float
    created_at: datetime
    total_items: int = 0

    model_config = {"from_attributes": True}
