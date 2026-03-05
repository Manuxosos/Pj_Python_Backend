"""
MODELO DE PROYECTO
===================
Un proyecto agrupa tareas relacionadas.
Tiene un propietario (manager o admin) y múltiples miembros.

RELACIONES:
  Proyecto → Tarea: Un proyecto tiene muchas tareas (OneToMany)
  Proyecto → Usuario: Un proyecto tiene un owner (ManyToOne)
"""

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base


class EstadoProyecto(str, enum.Enum):
    """Estado actual del proyecto."""
    PLANIFICACION = "PLANIFICACION"
    ACTIVO = "ACTIVO"
    EN_PAUSA = "EN_PAUSA"
    COMPLETADO = "COMPLETADO"
    CANCELADO = "CANCELADO"


class Proyecto(Base):
    """
    Tabla 'proyectos' en la base de datos.

    Un proyecto es la unidad de trabajo principal.
    Contiene tareas y tiene un responsable (owner).
    """

    __tablename__ = "proyectos"

    # --- Columnas ---
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(200), nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    estado = Column(
        SAEnum(EstadoProyecto),
        default=EstadoProyecto.PLANIFICACION,
        nullable=False
    )
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin_estimada = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- Clave foránea (Foreign Key) ---
    # owner_id referencia al campo 'id' de la tabla 'usuarios'
    # Equivale a @ManyToOne + @JoinColumn en JPA
    owner_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    # --- Relaciones ---
    # El dueño del proyecto
    owner = relationship(
        "Usuario",
        foreign_keys=[owner_id],
        back_populates="proyectos_creados"
    )

    # Las tareas del proyecto
    # cascade="all, delete-orphan": si se borra el proyecto, se borran sus tareas
    # Equivale a @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true) en JPA
    tareas = relationship(
        "Tarea",
        back_populates="proyecto",
        cascade="all, delete-orphan",
        order_by="Tarea.created_at"
    )

    def __repr__(self):
        return f"<Proyecto id={self.id} nombre='{self.nombre}' estado={self.estado}>"
