"""
UTILIDADES JWT (JSON Web Tokens)
==================================
Equivale a JwtUtil.java en el proyecto Spring Boot.

¿Qué es un JWT?
  Es un token que contiene información del usuario firmada digitalmente.
  Estructura: header.payload.signature (separados por puntos)

  Ejemplo:
  eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyQGVtYWlsLmNvbSJ9.FIRMA

FLUJO DE AUTENTICACIÓN:
  1. Cliente envía email + password
  2. Server verifica credenciales
  3. Server genera JWT y lo devuelve
  4. Cliente guarda el JWT (en localStorage o cookies)
  5. Cliente envía el JWT en cada petición: Authorization: Bearer <token>
  6. Server verifica el JWT en cada petición

La verificación del JWT es STATELESS: el server no guarda sesión,
toda la información está en el propio token.
"""

from datetime import datetime, timedelta, timezone
from typing import Any
from jose import JWTError, jwt
from app.config.settings import get_settings
from app.schemas.auth import TokenData

settings = get_settings()


def create_access_token(data: dict[str, Any]) -> str:
    """
    Crea un JWT con los datos del usuario.

    Args:
        data: Diccionario con datos a incluir en el token
              (email, usuario_id, rol)

    Returns:
        String del JWT firmado

    Ejemplo de uso:
        token = create_access_token({
            "sub": "user@email.com",
            "usuario_id": 1,
            "rol": "ADMIN"
        })
    """
    to_encode = data.copy()

    # Calcular cuándo expira el token
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})

    # Firmar el token con la clave secreta
    # jwt.encode() genera el string del token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """
    Verifica y decodifica un JWT.

    Si el token es inválido o expiró, lanza JWTError.

    Args:
        token: El string JWT del header Authorization

    Returns:
        TokenData con la información del usuario

    Raises:
        JWTError: Si el token es inválido, expirado o manipulado
    """
    # jwt.decode() verifica la firma Y la expiración automáticamente
    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm]
    )

    # Extraer datos del payload
    email: str = payload.get("sub")
    usuario_id: int = payload.get("usuario_id")
    rol: str = payload.get("rol")

    if email is None:
        raise JWTError("Token inválido: falta el email")

    return TokenData(email=email, usuario_id=usuario_id, rol=rol)
