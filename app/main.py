"""
PUNTO DE ENTRADA - ShopFlow API
=================================
Backend completo de tienda online.

PARA EJECUTAR:
  uvicorn app.main:app --reload

URLS:
  http://localhost:8000/docs      → Swagger UI
  http://localhost:8000/redoc     → ReDoc
  http://localhost:8000           → Info de la API
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.database import engine, Base, SessionLocal
from app.config.settings import get_settings

# Importar todos los modelos para que SQLAlchemy cree las tablas
from app.models import usuario, categoria, producto, carrito, pedido  # noqa: F401

# Routers (controllers)
from app.routers import auth, usuarios, categorias, productos, carrito as carrito_router, pedidos

from app.utils.data_initializer import inicializar_datos
from app.exceptions.handlers import registrar_handlers

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicio y cierre de la aplicación."""
    print(f"\n{'='*50}")
    print(f"  {settings.app_name} v{settings.app_version}")
    print(f"{'='*50}\n")

    # Crear tablas
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas en la base de datos")

    # Datos de prueba
    db = SessionLocal()
    try:
        inicializar_datos(db)
    finally:
        db.close()

    print(f"\n🚀 Servidor listo: http://localhost:8000")
    print(f"📚 Swagger UI:    http://localhost:8000/docs\n")

    yield

    print("\n👋 Cerrando ShopFlow API...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## ShopFlow API — Backend de Tienda Online

API REST completa que soporta una tienda online con carrito de compra, pedidos y gestión de catálogo.

### ¿Cómo usar esta API?

**1. Login (obtener token):**
```
POST /api/auth/login
{"email": "admin@shopflow.com", "password": "Admin1234"}
```

**2. Copiar el `access_token` y hacer clic en Authorize 🔒**

**3. ¡Explorar los endpoints!**

---

### Usuarios de prueba

| Email | Password | Rol |
|-------|----------|-----|
| `admin@shopflow.com` | `Admin1234` | ADMIN |
| `cliente1@email.com` | `Cliente1234` | CLIENTE (tiene carrito con items) |
| `cliente2@email.com` | `Cliente1234` | CLIENTE (tiene pedido entregado) |

---

### Endpoints públicos (sin autenticación)

| Método | URL | Descripción |
|--------|-----|-------------|
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/registro` | Crear cuenta |
| GET | `/api/productos/` | Catálogo con filtros |
| GET | `/api/productos/{id}` | Detalle de producto |
| GET | `/api/categorias/` | Listado de categorías |

### Endpoints de cliente (requieren JWT)

| Método | URL | Descripción |
|--------|-----|-------------|
| GET | `/api/carrito/` | Ver mi carrito |
| POST | `/api/carrito/items` | Añadir al carrito |
| POST | `/api/pedidos/` | Confirmar pedido (checkout) |
| GET | `/api/pedidos/mis-pedidos` | Mi historial |

### Endpoints de admin (requieren JWT + rol ADMIN)

| Método | URL | Descripción |
|--------|-----|-------------|
| POST | `/api/productos/` | Crear producto |
| PUT | `/api/productos/{id}` | Actualizar producto |
| PATCH | `/api/pedidos/{id}/estado` | Gestionar pedido |
| GET | `/api/usuarios/` | Ver todos los clientes |
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS: permite que React/Vue/Angular en otro puerto hagan peticiones
# En desarrollo: allow_origins=["*"]
# En producción: allow_origins=["https://tutienda.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar todos los routers
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(categorias.router)
app.include_router(productos.router)
app.include_router(carrito_router.router)
app.include_router(pedidos.router)

# Manejadores de errores globales
registrar_handlers(app)


@app.get("/", tags=["🏠 Info"], summary="Información de la API")
def root():
    """Endpoint raíz con información de la API."""
    return {
        "api": settings.app_name,
        "version": settings.app_version,
        "docs": "http://localhost:8000/docs",
        "endpoints_publicos": {
            "catalogo": "/api/productos/",
            "categorias": "/api/categorias/",
            "login": "/api/auth/login",
            "registro": "/api/auth/registro"
        }
    }


@app.get("/health", tags=["🏠 Info"], summary="Health check")
def health():
    """Monitoreo del servidor (como /actuator/health en Spring)."""
    return {"status": "ok", "version": settings.app_version}
