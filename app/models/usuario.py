"""
MODELO DE USUARIO
==================
Equivale a la clase @Entity Usuario de JPA en Java.

SQLAlchemy mapea esta clase Python a una tabla en la base de datos.
Cada atributo de clase = una columna en la tabla.

COMPARACIÓN CON JAVA/JPA:
  @Entity               → heredar de Base
  @Table(name="...")    → __tablename__
  @Id @GeneratedValue   → Column(primary_key=True)
  @Column(...)          → Column(...)
  @ManyToOne            → relationship(...)
  @Enumerated           → SQLAlchemy Enum type
"""

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.config.database import Base


# ==============================================================
# ENUMERACIONES - Valores posibles para campos específicos
# ==============================================================
class RolUsuario(str, enum.Enum):
    """
    Roles del sistema. 'str' permite comparar directamente con strings.
    Equivale al @Enumerated(EnumType.STRING) de JPA.
    """
    ADMIN = "ADMIN"           # Administrador del sistema
    MANAGER = "MANAGER"       # Jefe de proyecto
    DESARROLLADOR = "DESARROLLADOR"  # Desarrollador


# ==============================================================
# MODELO USUARIO
# ==============================================================
class Usuario(Base):
    """
    Tabla 'usuarios' en la base de datos.

    Columnas:
        id          → clave primaria autoincremental
        email       → único, es el nombre de usuario para login
        nombre      → nombre completo
        hashed_password → contraseña hasheada (NUNCA texto plano)
        rol         → rol del usuario (ADMIN, MANAGER, DESARROLLADOR)
        activo      → si la cuenta está activa (soft delete)
        created_at  → fecha de creación
        updated_at  → fecha de última modificación
    """

    __tablename__ = "usuarios"  # Nombre de la tabla en la BD

    # --- Columnas ---
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    rol = Column(SAEnum(RolUsuario), default=RolUsuario.DESARROLLADOR, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- Relaciones ---
    # Un usuario puede ser dueño de muchos proyectos
    # back_populates conecta la relación en ambos lados
    proyectos_creados = relationship(
        "Proyecto",
        foreign_keys="Proyecto.owner_id",
        back_populates="owner"
    )

    # Un usuario puede tener muchas tareas asignadas
    tareas_asignadas = relationship(
        "Tarea",
        foreign_keys="Tarea.asignado_a_id",
        back_populates="asignado_a"
    )

    # Un usuario puede crear muchos comentarios
    comentarios = relationship("Comentario", back_populates="autor")

    def __repr__(self):
        """Representación legible del objeto (como toString() en Java)"""
        return f"<Usuario id={self.id} email='{self.email}' rol={self.rol}>"
