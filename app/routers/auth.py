"""
ROUTER DE AUTENTICACIÓN
=========================
Equivale a AuthController.java en Spring Boot.

En FastAPI, los "routers" son los "controllers" de Java/Spring.
Definen los endpoints (URLs) y métodos HTTP.

COMPARACIÓN CON SPRING:
  @RestController    → APIRouter()
  @RequestMapping    → prefix="/api/auth"
  @PostMapping       → @router.post(...)
  @RequestBody       → Pydantic schema en parámetro

ENDPOINTS:
  POST /api/auth/login  → Obtener JWT
  GET  /api/auth/me     → Ver usuario actual

DOCUMENTACIÓN AUTOMÁTICA:
  FastAPI genera Swagger/OpenAPI automáticamente.
  No necesitas Springdoc ni ninguna librería extra.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.usuario import UsuarioResponse
from app.security.dependencies import get_usuario_actual
from app.models.usuario import Usuario
from app.services import auth_service

# APIRouter = @RestController + @RequestMapping en Spring
router = APIRouter(
    prefix="/api/auth",    # Prefijo común para todos los endpoints
    tags=["🔐 Autenticación"],  # Agrupa los endpoints en Swagger UI
)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
    description="""
    Autentica al usuario con email y contraseña.
    Devuelve un JWT Bearer Token para usar en las demás peticiones.

    **Usuarios de prueba:**
    - admin@taskflow.com / Admin1234 (ADMIN)
    - laura@taskflow.com / Manager1234 (MANAGER)
    - carlos@taskflow.com / Dev1234 (DESARROLLADOR)
    """
)
def login(
    login_data: LoginRequest,   # Pydantic valida automáticamente el body JSON
    db: Session = Depends(get_db)  # Inyección de dependencia (como @Autowired)
):
    """
    Endpoint de login. Devuelve el JWT si las credenciales son correctas.

    Cómo usar el token recibido:
        Authorization: Bearer <access_token>
    """
    return auth_service.login(db, login_data)


@router.get(
    "/me",
    response_model=UsuarioResponse,
    summary="Ver mi perfil",
    description="Devuelve los datos del usuario actualmente autenticado."
)
def get_mi_perfil(
    # Depends(get_usuario_actual) = @PreAuthorize("isAuthenticated()") en Spring
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    """
    Endpoint protegido: requiere JWT válido.
    FastAPI verifica el token automáticamente con get_usuario_actual.
    """
    return usuario_actual
