"""
MODELO DE PEDIDO
=================
Un pedido es la confirmación de una compra.

FLUJO DE ESTADOS:
  PENDIENTE → CONFIRMADO → ENVIADO → ENTREGADO
                         ↓
                      CANCELADO (desde cualquier estado antes de ENVIADO)

IMPORTANTE - ¿Por qué guardar el precio en el PedidoItem?
  El precio de un producto PUEDE CAMBIAR en el futuro.
  Si un producto costaba 99€ cuando lo compraste, y ahora cuesta 149€,
  tu factura debe seguir mostrando 99€.

  Por eso PedidoItem guarda 'precio_unitario' en el momento de la compra.
  Es una "foto" del precio en ese instante.

  Esto es un patrón de diseño llamado "historical data" o "snapshot".
  Lo usan todos los e-commerce del mundo.
"""

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base


class EstadoPedido(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADO = "CONFIRMADO"
    ENVIADO = "ENVIADO"
    ENTREGADO = "ENTREGADO"
    CANCELADO = "CANCELADO"


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    estado = Column(SAEnum(EstadoPedido), default=EstadoPedido.PENDIENTE, nullable=False)
    total = Column(Float, nullable=False)                    # Total en el momento de la compra
    direccion_envio = Column(Text, nullable=False)           # Dirección guardada en el pedido
    notas = Column(Text, nullable=True)                      # Notas del cliente
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    usuario = relationship("Usuario", back_populates="pedidos")
    items = relationship(
        "PedidoItem",
        back_populates="pedido",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Pedido id={self.id} estado={self.estado} total={self.total}€>"


class PedidoItem(Base):
    """
    Un producto dentro de un pedido.
    Guarda el precio en el momento de la compra (snapshot).
    """
    __tablename__ = "pedido_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)  # Precio en el momento de compra
    nombre_producto = Column(String(300), nullable=False)  # Snapshot del nombre

    pedido = relationship("Pedido", back_populates="items")
    producto = relationship("Producto", back_populates="items_pedido")

    @property
    def subtotal(self) -> float:
        return self.precio_unitario * self.cantidad

    def __repr__(self):
        return f"<PedidoItem producto='{self.nombre_producto}' x{self.cantidad}>"
