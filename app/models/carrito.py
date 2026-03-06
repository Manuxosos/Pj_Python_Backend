"""
MODELO DE CARRITO
==================
El carrito de compra es persistente en la BD (no en sesión del navegador).

¿Por qué persistente en BD y no en el navegador (localStorage)?
  - El usuario puede cambiar de dispositivo y seguir con su carrito
  - El backend puede calcular precios actualizados en tiempo real
  - Permite recuperar carritos abandonados (estrategia de marketing)
  - Amazon, Zara, El Corte Inglés... todos usan carritos persistentes

ESTRUCTURA:
  Carrito (1) → (N) CarritoItem → Producto
  Un carrito tiene items. Cada item referencia un producto y una cantidad.

RELACIÓN ESPECIAL:
  Carrito ↔ Usuario es 1:1 (cada usuario tiene exactamente un carrito)
  El carrito se crea cuando el usuario se registra.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.config.database import Base


class Carrito(Base):
    __tablename__ = "carritos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), unique=True, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    usuario = relationship("Usuario", back_populates="carrito")
    items = relationship(
        "CarritoItem",
        back_populates="carrito",
        cascade="all, delete-orphan"  # Al borrar el carrito, se borran sus items
    )

    @property
    def total(self) -> float:
        """Calcula el total del carrito sumando precio × cantidad de cada item."""
        return sum(item.subtotal for item in self.items)

    @property
    def total_items(self) -> int:
        """Total de unidades en el carrito (no tipos, sino unidades)."""
        return sum(item.cantidad for item in self.items)

    def __repr__(self):
        return f"<Carrito id={self.id} usuario_id={self.usuario_id} items={len(self.items)}>"


class CarritoItem(Base):
    """
    Un item dentro del carrito.
    Representa 'X unidades del Producto Y en el carrito'.
    """
    __tablename__ = "carrito_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    carrito_id = Column(Integer, ForeignKey("carritos.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, default=1, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relaciones
    carrito = relationship("Carrito", back_populates="items")
    producto = relationship("Producto", back_populates="items_carrito")

    @property
    def subtotal(self) -> float:
        """Precio del item: precio_final × cantidad."""
        return self.producto.precio_final * self.cantidad

    def __repr__(self):
        return f"<CarritoItem producto_id={self.producto_id} cantidad={self.cantidad}>"
