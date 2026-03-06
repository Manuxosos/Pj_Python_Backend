"""
SERVICIO DE PEDIDOS
====================
La operación más crítica: convertir un carrito en un pedido.

TRANSACCIÓN COMPLETA al confirmar pedido:
  1. Verificar carrito no vacío
  2. Verificar stock de cada producto
  3. Crear el Pedido con snapshot de precios
  4. Crear los PedidoItems con snapshot de precios
  5. Decrementar stock de cada producto
  6. Vaciar el carrito
  7. Commit (todo o nada)

Si cualquier paso falla → rollback automático de SQLAlchemy.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.pedido import Pedido, PedidoItem, EstadoPedido
from app.models.carrito import Carrito
from app.models.usuario import Usuario, RolUsuario
from app.schemas.pedido import CrearPedidoRequest, ActualizarEstadoPedidoRequest


def get_mis_pedidos(db: Session, usuario: Usuario) -> list[Pedido]:
    """Los pedidos del usuario actual, del más reciente al más antiguo."""
    return db.query(Pedido).filter(
        Pedido.usuario_id == usuario.id
    ).order_by(Pedido.created_at.desc()).all()


def get_all(db: Session) -> list[Pedido]:
    """Todos los pedidos (solo ADMIN)."""
    return db.query(Pedido).order_by(Pedido.created_at.desc()).all()


def get_by_id(db: Session, pedido_id: int, usuario: Usuario) -> Pedido:
    """
    Busca un pedido. El cliente solo puede ver sus propios pedidos.
    El ADMIN puede ver cualquiera.
    """
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido con ID {pedido_id} no encontrado"
        )

    if usuario.rol == RolUsuario.CLIENTE and pedido.usuario_id != usuario.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a este pedido"
        )
    return pedido


def confirmar_pedido(
    db: Session,
    usuario: Usuario,
    datos: CrearPedidoRequest
) -> Pedido:
    """
    Convierte el carrito actual en un pedido confirmado.

    Este es el proceso de CHECKOUT completo.
    Toda la operación es atómica: si algo falla, nada se guarda.
    """
    # 1. Obtener el carrito
    carrito = db.query(Carrito).filter(Carrito.usuario_id == usuario.id).first()

    if not carrito or len(carrito.items) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El carrito está vacío. Añade productos antes de confirmar el pedido."
        )

    # 2. Verificar stock de todos los productos ANTES de procesar
    for item in carrito.items:
        if item.producto.stock < item.cantidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente para '{item.producto.nombre}'. "
                       f"Solicitado: {item.cantidad}, Disponible: {item.producto.stock}"
            )

    # 3. Calcular total
    total = sum(item.subtotal for item in carrito.items)

    # 4. Crear el Pedido
    nuevo_pedido = Pedido(
        usuario_id=usuario.id,
        total=round(total, 2),
        estado=EstadoPedido.PENDIENTE,
        direccion_envio=datos.direccion_envio,
        notas=datos.notas
    )
    db.add(nuevo_pedido)
    db.flush()  # Necesitamos el ID del pedido antes de crear los items

    # 5. Crear PedidoItems con SNAPSHOT de precios y nombres
    #    (importante: guardamos el precio actual, no el ID del producto)
    for item in carrito.items:
        pedido_item = PedidoItem(
            pedido_id=nuevo_pedido.id,
            producto_id=item.producto_id,
            cantidad=item.cantidad,
            precio_unitario=item.producto.precio_final,  # Snapshot del precio actual
            nombre_producto=item.producto.nombre         # Snapshot del nombre actual
        )
        db.add(pedido_item)

        # 6. Decrementar stock del producto
        item.producto.stock -= item.cantidad

    # 7. Vaciar el carrito
    for item in carrito.items:
        db.delete(item)

    # 8. Commit atómico: todo se guarda junto o nada
    db.commit()
    db.refresh(nuevo_pedido)
    return nuevo_pedido


def actualizar_estado(
    db: Session,
    pedido_id: int,
    datos: ActualizarEstadoPedidoRequest,
    admin: Usuario
) -> Pedido:
    """
    Cambia el estado del pedido. Solo ADMIN.

    El ADMIN actualiza manualmente: PENDIENTE → CONFIRMADO → ENVIADO → ENTREGADO
    En producción esto se integra con sistemas logísticos (DHL, SEUR, etc.)
    """
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido {pedido_id} no encontrado"
        )

    # Regla: no se puede cambiar estado de un pedido ENTREGADO
    if pedido.estado == EstadoPedido.ENTREGADO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede modificar un pedido ya entregado"
        )

    # Si se cancela, devolver el stock
    if datos.estado == EstadoPedido.CANCELADO and pedido.estado != EstadoPedido.CANCELADO:
        for item in pedido.items:
            item.producto.stock += item.cantidad

    pedido.estado = datos.estado
    db.commit()
    db.refresh(pedido)
    return pedido
