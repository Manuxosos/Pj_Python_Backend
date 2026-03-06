"""
MODELO DE CATEGORÍA
====================
Las categorías organizan el catálogo de productos.

En una tienda real: Electrónica, Ropa, Hogar, Deportes, etc.
El frontend usa esto para el menú de navegación y los filtros.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.config.database import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), unique=True, nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    icono = Column(String(50), nullable=True)   # Nombre del icono (ej: "laptop", "shirt")
    activo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Una categoría tiene muchos productos
    productos = relationship("Producto", back_populates="categoria")

    def __repr__(self):
        return f"<Categoria id={self.id} nombre='{self.nombre}'>"
