"""
MODELO DE TAREA
================
Una tarea es la unidad mínima de trabajo dentro de un proyecto.
Puede estar asignada a un usuario y tiene estados/prioridades.

RELACIONES:
  Tarea → Proyecto: ManyToOne (muchas tareas en un proyecto)
  Tarea → Usuario: ManyToOne (asignada a un usuario)
  Tarea → Comentario: OneToMany (una tarea tiene muchos comentarios)
"""

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base


class EstadoTarea(str, enum.Enum):
    """Ciclo de vida de una tarea (workflow)."""
    PENDIENTE = "PENDIENTE"
    EN_PROGRESO = "EN_PROGRESO"
    EN_REVISION = "EN_REVISION"
    COMPLETADA = "COMPLETADA"
    CANCELADA = "CANCELADA"


class PrioridadTarea(str, enum.Enum):
    """Nivel de urgencia/importancia de la tarea."""
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"


class Tarea(Base):
    """
    Tabla 'tareas' en la base de datos.

    Una tarea pertenece a un proyecto, puede estar asignada
    a un usuario, y tiene comentarios asociados.
    """

    __tablename__ = "tareas"

    # --- Columnas ---
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo = Column(String(300), nullable=False)
    descripcion = Column(Text, nullable=True)
    estado = Column(
        SAEnum(EstadoTarea),
        default=EstadoTarea.PENDIENTE,
        nullable=False,
        index=True
    )
    prioridad = Column(
        SAEnum(PrioridadTarea),
        default=PrioridadTarea.MEDIA,
        nullable=False
    )
    fecha_limite = Column(DateTime, nullable=True)
    fecha_completada = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- Claves foráneas ---
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"), nullable=False)
    asignado_a_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)  # Puede no tener asignado
    creado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    # --- Relaciones ---
    proyecto = relationship("Proyecto", back_populates="tareas")

    asignado_a = relationship(
        "Usuario",
        foreign_keys=[asignado_a_id],
        back_populates="tareas_asignadas"
    )

    creado_por = relationship(
        "Usuario",
        foreign_keys=[creado_por_id]
    )

    comentarios = relationship(
        "Comentario",
        back_populates="tarea",
        cascade="all, delete-orphan",
        order_by="Comentario.created_at"
    )

    def __repr__(self):
        return f"<Tarea id={self.id} titulo='{self.titulo}' estado={self.estado}>"
