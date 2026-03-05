"""
CONFIGURACIÓN DE LA BASE DE DATOS
====================================
Equivale a la configuración de DataSource en Spring Boot.

SQLAlchemy es el ORM (Object-Relational Mapper) de Python.
Es equivalente a JPA/Hibernate en Java.

CONCEPTOS CLAVE:
- Engine: La conexión a la base de datos
- Session: Una "transacción" con la BD (como EntityManager en JPA)
- Base: Clase padre de todos los modelos (como @Entity en JPA)

FLUJO:
  Request → FastAPI → get_db() → Operaciones DB → Cerrar sesión → Response
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config.settings import get_settings

settings = get_settings()

# ==============================================================
# 1. MOTOR DE BASE DE DATOS (Engine)
# ==============================================================
# El Engine es el punto de conexión a la BD.
# connect_args={"check_same_thread": False} es solo para SQLite
# (SQLite no permite usar la misma conexión en múltiples threads por defecto)

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # Solo para SQLite
    echo=settings.debug,  # Si debug=True, imprime el SQL generado (como show-sql en Spring)
)

# ==============================================================
# 2. FÁBRICA DE SESIONES (SessionLocal)
# ==============================================================
# SessionLocal crea instancias de Session para cada request.
# autocommit=False: las transacciones deben confirmarse manualmente
# autoflush=False:  los cambios no se envían a la BD hasta el commit

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==============================================================
# 3. CLASE BASE PARA MODELOS
# ==============================================================
class Base(DeclarativeBase):
    """
    Clase base que heredan todos los modelos de la aplicación.
    Equivale a @Entity (la parte estructural) en JPA.

    Al heredar de esta clase, SQLAlchemy sabe que la clase
    es una tabla en la base de datos.
    """
    pass


# ==============================================================
# 4. DEPENDENCIA PARA INYECTAR LA SESIÓN
# ==============================================================
def get_db():
    """
    Generador que provee una sesión de BD por request.

    Con 'yield', FastAPI:
    1. Crea la sesión ANTES del endpoint
    2. Ejecuta el endpoint
    3. Cierra la sesión DESPUÉS del endpoint (con o sin errores)

    Equivale al @Transactional de Spring, pero manual.

    Uso en routers:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db          # FastAPI inyecta esta sesión en el endpoint
    finally:
        db.close()        # Siempre se cierra, incluso si hay error
