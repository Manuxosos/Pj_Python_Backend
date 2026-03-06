"""
ROUTER DE PEDIDOS
==================
El checkout y la gestión de pedidos.

CLIENTE puede:
  POST /api/pedidos/          → Confirmar pedido (checkout)
  GET  /api/pedidos/mis-pedidos → Ver su historial de compras
  GET  /api/pedidos/{id}      → Ver detalle de un pedido suyo

ADMIN puede:
  GET  /api/pedidos/           → Ver todos los pedidos
  PATCH /api/pedidos/{id}/estado → Actualizar estado (CONFIRMADO → ENVIADO → ENTREGADO)

FLUJO DE CHECKOUT EN EL FRONTEND:
  1. Usuario pulsa "Ir al checkout" desde el carrito
  2. Frontend muestra formulario de dirección de envío
  3. Usuario introduce dirección y pulsa "Confirmar pedido"
  4. Frontend: POST /api/pedidos/ {"direccion_envio": "Calle...", "notas": "..."}
  5. Backend procesa el pedido (transacción completa)
  6. Frontend: redirige a /pedido-confirmado/{id}
  7. Frontend muestra: "¡Gracias! Pedido #1234 confirmado"
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.usuario import Usuario
from app.schemas.pedido import (
    CrearPedidoRequest, ActualizarEstadoPedidoRequest,
    PedidoResponse, PedidoResumenResponse, PedidoItemResponse
)
from app.security.dependencies import get_usuario_actual, require_admin
from app.services import pedido_service

router = APIRouter(prefix="/api/pedidos", tags=["📦 Pedidos"])


def _pedido_to_response(pedido) -> PedidoResponse:
    """Convierte el modelo Pedido en schema de respuesta."""
    return PedidoResponse(
        id=pedido.id,
        estado=pedido.estado,
        total=pedido.total,
        direccion_envio=pedido.direccion_envio,
        notas=pedido.notas,
        created_at=pedido.created_at,
        updated_at=pedido.updated_at,
        items=[
            PedidoItemResponse(
                id=item.id,
                producto_id=item.producto_id,
                nombre_producto=item.nombre_producto,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario,
                subtotal=item.subtotal
            )
            for item in pedido.items
        ],
        usuario={
            "id": pedido.usuario.id,
            "nombre": pedido.usuario.nombre,
            "apellido": pedido.usuario.apellido,
            "email": pedido.usuario.email
        }
    )


@router.get(
    "/mis-pedidos",
    response_model=list[PedidoResumenResponse],
    summary="Mi historial de pedidos"
)
def mis_pedidos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """
    Historial de compras del usuario autenticado.
    El frontend lo muestra en "Mi cuenta → Mis pedidos".
    """
    pedidos = pedido_service.get_mis_pedidos(db, usuario)
    return [
        PedidoResumenResponse(
            id=p.id,
            estado=p.estado,
            total=p.total,
            created_at=p.created_at,
            total_items=sum(i.cantidad for i in p.items)
        )
        for p in pedidos
    ]


@router.post(
    "/",
    response_model=PedidoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Confirmar pedido (checkout)",
    description="""
Convierte el carrito actual en un pedido.

**Proceso:**
1. Verifica que el carrito no está vacío
2. Verifica stock de todos los productos
3. Crea el pedido con snapshot de precios
4. Descuenta stock de cada producto
5. Vacía el carrito

**Si algo falla:** Todo se revierte (transacción atómica).
    """
)
def confirmar_pedido(
    datos: CrearPedidoRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    pedido = pedido_service.confirmar_pedido(db, usuario, datos)
    return _pedido_to_response(pedido)


@router.get(
    "/{pedido_id}",
    response_model=PedidoResponse,
    summary="Ver detalle de pedido"
)
def ver_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """El cliente solo ve sus propios pedidos. ADMIN ve cualquiera."""
    pedido = pedido_service.get_by_id(db, pedido_id, usuario)
    return _pedido_to_response(pedido)


@router.get("/", response_model=list[PedidoResumenResponse], summary="Todos los pedidos")
def todos_los_pedidos(
    db: Session = Depends(get_db),
    _admin: Usuario = Depends(require_admin)
):
    """Solo ADMIN. Panel de gestión de pedidos."""
    pedidos = pedido_service.get_all(db)
    return [
        PedidoResumenResponse(
            id=p.id, estado=p.estado, total=p.total,
            created_at=p.created_at,
            total_items=sum(i.cantidad for i in p.items)
        )
        for p in pedidos
    ]


@router.patch(
    "/{pedido_id}/estado",
    response_model=PedidoResponse,
    summary="Actualizar estado del pedido"
)
def actualizar_estado(
    pedido_id: int,
    datos: ActualizarEstadoPedidoRequest,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(require_admin)
):
    """
    Solo ADMIN actualiza el estado: PENDIENTE → CONFIRMADO → ENVIADO → ENTREGADO.
    En producción esto se conecta con APIs de mensajería y logística.
    """
    pedido = pedido_service.actualizar_estado(db, pedido_id, datos, admin)
    return _pedido_to_response(pedido)
