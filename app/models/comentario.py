"""
MODELO DE COMENTARIO
=====================
Los comentarios se añaden a las tareas para comunicación del equipo.

RELACIONES:
  Comentario → Tarea: ManyToOne
  Comentario → Usuario (autor): ManyToOne
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base


class Comentario(Base):
    """
    Tabla 'comentarios' en la base de datos.
    """

    __tablename__ = "comentarios"

    # --- Columnas ---
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    contenido = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- Claves foráneas ---
    tarea_id = Column(Integer, ForeignKey("tareas.id"), nullable=False)
    autor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    # --- Relaciones ---
    tarea = relationship("Tarea", back_populates="comentarios")
    autor = relationship("Usuario", back_populates="comentarios")

    def __repr__(self):
        return f"<Comentario id={self.id} tarea_id={self.tarea_id}>"
