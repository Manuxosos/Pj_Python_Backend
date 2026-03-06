"""
MODELO DE PRODUCTO
===================
El núcleo del e-commerce. Un producto tiene:
  - Información descriptiva (nombre, descripción, imagen)
  - Precio
  - Stock (inventario disponible)
  - Categoría (para organización y filtros)

CONCEPTO IMPORTANTE - Stock:
  Cuando un cliente hace un pedido, el stock baja.
  Si el stock llega a 0, el producto no se puede añadir al carrito.
  Esta lógica la gestiona el servicio (capa de negocio), no el modelo.

DATO REAL:
  Amazon tiene más de 300 millones de productos activos.
  Cada operación de compra requiere verificar y decrementar el stock
  de forma atómica (sin race conditions).
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(300), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    precio = Column(Float, nullable=False)               # En euros
    precio_descuento = Column(Float, nullable=True)      # Precio con oferta
    stock = Column(Integer, default=0, nullable=False)   # Unidades disponibles
    imagen_url = Column(String(500), nullable=True)      # URL de la imagen
    activo = Column(Boolean, default=True, nullable=False)
    destacado = Column(Boolean, default=False, nullable=False)  # Para el home del frontend
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Clave foránea → pertenece a una categoría
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)

    # Relaciones
    categoria = relationship("Categoria", back_populates="productos")
    items_carrito = relationship("CarritoItem", back_populates="producto")
    items_pedido = relationship("PedidoItem", back_populates="producto")

    @property
    def precio_final(self) -> float:
        """Precio real (con descuento si lo hay). Propiedad calculada."""
        return self.precio_descuento if self.precio_descuento else self.precio

    @property
    def tiene_descuento(self) -> bool:
        """True si el producto tiene precio de descuento activo."""
        return self.precio_descuento is not None and self.precio_descuento < self.precio

    def __repr__(self):
        return f"<Producto id={self.id} nombre='{self.nombre}' precio={self.precio}€>"
