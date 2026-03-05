"""
PUNTO DE ENTRADA DE LA APLICACIÓN
====================================
Equivale a la clase @SpringBootApplication de Spring Boot.

Este es el archivo principal que:
1. Crea la aplicación FastAPI
2. Configura middleware (CORS, etc.)
3. Registra los routers (controllers)
4. Crea las tablas de la BD
5. Carga los datos de prueba

PARA EJECUTAR:
  uvicorn app.main:app --reload

URLS IMPORTANTES:
  http://localhost:8000           → API
  http://localhost:8000/docs      → Swagger UI (documentación interactiva)
  http://localhost:8000/redoc     → ReDoc (documentación alternativa)
  http://localhost:8000/openapi.json → Spec OpenAPI en JSON
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.database import engine, Base, SessionLocal
from app.config.settings import get_settings

# Importar modelos para que SQLAlchemy los conozca al crear tablas
from app.models import usuario, proyecto, tarea, comentario  # noqa: F401

# Importar routers
from app.routers import auth, usuarios, proyectos, tareas, comentarios

# Importar inicializador de datos
from app.utils.data_initializer import inicializar_datos

# Importar manejadores de excepciones
from app.exceptions.handlers import registrar_handlers

settings = get_settings()


# ==============================================================
# LIFESPAN (Eventos de inicio y cierre)
# ==============================================================
# Equivale a @PostConstruct y @PreDestroy en Spring Boot
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Código que se ejecuta al INICIAR la aplicación.
    (Todo lo que está antes del 'yield')

    Código que se ejecuta al CERRAR la aplicación.
    (Todo lo que está después del 'yield')
    """
    # ---- AL INICIAR ----
    print(f"\n{'='*50}")
    print(f"  {settings.app_name} v{settings.app_version}")
    print(f"{'='*50}")
    print(f"  Modo debug: {settings.debug}")
    print(f"  Base de datos: {settings.database_url}")
    print(f"{'='*50}\n")

    # Crear tablas en la BD (como Hibernate DDL auto=create en Spring)
    # En producción usarías Alembic para migraciones controladas
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas/verificadas en la base de datos")

    # Cargar datos de prueba
    db = SessionLocal()
    try:
        inicializar_datos(db)
    finally:
        db.close()

    print(f"\n🚀 Servidor listo en http://localhost:8000")
    print(f"📚 Swagger UI: http://localhost:8000/docs\n")

    yield  # La aplicación corre aquí

    # ---- AL CERRAR ----
    print("\n👋 Cerrando TaskFlow API...")


# ==============================================================
# CREAR APLICACIÓN FASTAPI
# ==============================================================
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## TaskFlow API - Sistema de Gestión de Proyectos

API REST completa para gestión de proyectos y tareas en equipo.

### Características
- 🔐 **Autenticación JWT** - Login seguro con tokens Bearer
- 👥 **Roles de usuario** - ADMIN, MANAGER, DESARROLLADOR
- 📁 **Proyectos** - Crear y gestionar proyectos
- ✅ **Tareas** - CRUD con estados y prioridades
- 💬 **Comentarios** - Comunicación en tareas
- 🛡️ **Seguridad** - Autorización basada en roles

### Cómo usar
1. Haz login en `/api/auth/login` con un usuario de prueba
2. Copia el `access_token` de la respuesta
3. Haz clic en **Authorize** 🔒 y pega el token
4. ¡Ya puedes usar todos los endpoints protegidos!

### Usuarios de prueba
| Email | Password | Rol |
|-------|----------|-----|
| admin@taskflow.com | Admin1234 | ADMIN |
| laura@taskflow.com | Manager1234 | MANAGER |
| carlos@taskflow.com | Dev1234 | DESARROLLADOR |
    """,
    lifespan=lifespan,
    # Configuración de OpenAPI (equivale a SpringDoc en Spring Boot)
    docs_url="/docs",          # Swagger UI
    redoc_url="/redoc",        # ReDoc
    openapi_url="/openapi.json"
)

# ==============================================================
# MIDDLEWARE CORS
# ==============================================================
# CORS (Cross-Origin Resource Sharing): permite que el frontend
# (en otro dominio/puerto) pueda hacer peticiones a esta API.
# Equivale a @CrossOrigin en Spring Boot o WebMvcConfigurer.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # En producción: ["https://tudominio.com"]
    allow_credentials=True,
    allow_methods=["*"],       # GET, POST, PUT, DELETE, PATCH, etc.
    allow_headers=["*"],       # Authorization, Content-Type, etc.
)

# ==============================================================
# REGISTRAR ROUTERS (Controllers)
# ==============================================================
# Equivale a la configuración de @RequestMapping en Spring MVC
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(proyectos.router)
app.include_router(tareas.router)
app.include_router(comentarios.router)

# ==============================================================
# REGISTRAR MANEJADORES DE EXCEPCIONES
# ==============================================================
registrar_handlers(app)

# ==============================================================
# ENDPOINTS RAÍZ
# ==============================================================
@app.get(
    "/",
    tags=["🏠 Inicio"],
    summary="Información de la API"
)
def root():
    """Endpoint de bienvenida con información básica de la API."""
    return {
        "api": settings.app_name,
        "version": settings.app_version,
        "documentacion": "http://localhost:8000/docs",
        "estado": "operativo",
        "endpoints": {
            "autenticacion": "/api/auth",
            "usuarios": "/api/usuarios",
            "proyectos": "/api/proyectos",
            "tareas": "/api/tareas",
        }
    }


@app.get(
    "/health",
    tags=["🏠 Inicio"],
    summary="Estado de salud del servidor"
)
def health_check():
    """
    Health check endpoint.
    Equivale a /actuator/health de Spring Boot Actuator.
    Usado por sistemas de monitoreo (Kubernetes, load balancers).
    """
    return {"status": "ok", "version": settings.app_version}
