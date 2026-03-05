"""
DEPENDENCIAS DE SEGURIDAD
===========================
Equivale a JwtAuthenticationFilter.java + @PreAuthorize de Spring Security.

En FastAPI, la autenticación se implementa como "dependencias".
Una dependencia es una función que FastAPI ejecuta ANTES del endpoint.

Si la dependencia falla (token inválido), FastAPI devuelve 401 automáticamente.
Si el usuario no tiene el rol correcto, devuelve 403.

COMPARACIÓN CON SPRING SECURITY:
  @PreAuthorize("isAuthenticated()")    → Depends(get_usuario_actual)
  @PreAuthorize("hasRole('ADMIN')")     → Depends(require_admin)
  @PreAuthorize("hasRole('MANAGER')")   → Depends(require_manager)
  SecurityContext.getAuthentication()   → usuario: Usuario = Depends(get_usuario_actual)

USO EN ENDPOINTS:
  @router.get("/protegido")
  def endpoint(usuario = Depends(get_usuario_actual)):
      # Solo llega aquí si el token es válido
      return {"usuario": usuario.nombre}
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.usuario import Usuario, RolUsuario
from app.security.jwt import verify_token

# OAuth2PasswordBearer:
#   - Define dónde está el token (en el header Authorization: Bearer <token>)
#   - Genera el "lock" icon en Swagger UI
#   - tokenUrl es el endpoint de login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_usuario_actual(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Dependencia principal de autenticación.

    FastAPI ejecuta esta función en cada endpoint que la use.
    Extrae y verifica el JWT del header Authorization.

    Raises:
        401 UNAUTHORIZED → Token inválido, expirado o ausente
        401 UNAUTHORIZED → Usuario no encontrado o inactivo
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decodificar y verificar el JWT
        token_data = verify_token(token)
    except JWTError:
        raise credentials_exception

    # Buscar el usuario en la BD
    usuario = db.query(Usuario).filter(
        Usuario.email == token_data.email
    ).first()

    if usuario is None:
        raise credentials_exception

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario desactivado"
        )

    return usuario


def require_admin(usuario: Usuario = Depends(get_usuario_actual)) -> Usuario:
    """
    Dependencia que exige rol ADMIN.
    Equivale a @PreAuthorize("hasRole('ADMIN')") en Spring.

    Raises:
        403 FORBIDDEN → Si el usuario no es ADMIN
    """
    if usuario.rol != RolUsuario.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    return usuario


def require_manager_or_admin(usuario: Usuario = Depends(get_usuario_actual)) -> Usuario:
    """
    Dependencia que exige rol MANAGER o ADMIN.
    Equivale a @PreAuthorize("hasAnyRole('ADMIN', 'MANAGER')") en Spring.
    """
    if usuario.rol not in [RolUsuario.ADMIN, RolUsuario.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de manager o administrador"
        )
    return usuario
