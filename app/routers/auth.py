"""
ROUTER DE AUTENTICACIÓN
=========================
POST /api/auth/login     → Obtener JWT
POST /api/auth/registro  → Registrar nueva cuenta (público)
GET  /api/auth/me        → Ver perfil del usuario autenticado
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.usuario import UsuarioRegistro, UsuarioResponse
from app.security.dependencies import get_usuario_actual
from app.models.usuario import Usuario
from app.services import auth_service, usuario_service

router = APIRouter(prefix="/api/auth", tags=["🔐 Autenticación"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
    description="""
Obtener JWT token. Úsalo en el botón **Authorize** 🔒 para acceder a los endpoints protegidos.

**Usuarios de prueba:**
| Email | Password | Rol |
|-------|----------|-----|
| admin@shopflow.com | Admin1234 | ADMIN |
| cliente1@email.com | Cliente1234 | CLIENTE |
| cliente2@email.com | Cliente1234 | CLIENTE |
    """
)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(db, login_data)


@router.post(
    "/registro",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear cuenta",
    description="Registro público. El rol siempre será CLIENTE."
)
def registrar(datos: UsuarioRegistro, db: Session = Depends(get_db)):
    """
    Endpoint PÚBLICO (sin JWT).
    Es el botón "Crear cuenta" del frontend de la tienda.
    """
    return usuario_service.registrar(db, datos)


@router.get(
    "/me",
    response_model=UsuarioResponse,
    summary="Mi perfil"
)
def get_mi_perfil(usuario_actual: Usuario = Depends(get_usuario_actual)):
    """Devuelve los datos del usuario autenticado con el JWT."""
    return usuario_actual
