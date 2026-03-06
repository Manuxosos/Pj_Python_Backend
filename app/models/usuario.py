"""
MODELO DE USUARIO
==================
En una tienda online hay dos tipos de usuarios:
  - ADMIN: gestiona el catálogo, procesa pedidos, ve estadísticas
  - CLIENTE: navega el catálogo, tiene carrito, hace pedidos

CONCEPTO CLAVE - Normalización de datos:
  Un usuario TIENE un carrito (1:1) y muchos pedidos (1:N).
  Cada tabla tiene una sola responsabilidad.
"""

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.config.database import Base


class RolUsuario(str, enum.Enum):
    ADMIN = "ADMIN"
    CLIENTE = "CLIENTE"


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    rol = Column(SAEnum(RolUsuario), default=RolUsuario.CLIENTE, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relación 1:1 → un usuario tiene UN solo carrito
    # uselist=False → devuelve objeto único en vez de lista
    carrito = relationship("Carrito", back_populates="usuario", uselist=False)

    # Relación 1:N → un usuario puede tener muchos pedidos
    pedidos = relationship("Pedido", back_populates="usuario")

    def __repr__(self):
        return f"<Usuario id={self.id} email='{self.email}' rol={self.rol}>"
