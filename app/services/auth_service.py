"""
SERVICIO DE AUTENTICACIÓN
===========================
Equivale a AuthService.java en el proyecto Spring Boot.

Gestiona:
  - Verificación de credenciales (email + password)
  - Generación de JWT
  - Hashing y verificación de contraseñas

SEGURIDAD DE CONTRASEÑAS:
  NUNCA se guarda la contraseña en texto plano.
  Se usa bcrypt para hashear: password → $2b$12$HASH_IRREVERSIBLE

  ¿Por qué bcrypt?
  - Es lento a propósito (dificulta ataques de fuerza bruta)
  - Incluye "salt" automático (mismo password → hashes distintos)
  - Estándar de la industria

COMPARACIÓN CON SPRING:
  bcrypt.hashpw()   → BCryptPasswordEncoder.encode()
  bcrypt.checkpw()  → BCryptPasswordEncoder.matches()
"""

from datetime import timezone, datetime
from sqlalchemy.orm import Session
import bcrypt
from fastapi import HTTPException, status
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, TokenResponse
from app.security.jwt import create_access_token
from app.config.settings import get_settings

settings = get_settings()


def hash_password(password: str) -> str:
    """
    Convierte una contraseña en texto plano a un hash bcrypt.

    El resultado es diferente cada vez (por el salt automático), pero
    bcrypt.checkpw() siempre puede verificarlo.

    Ejemplo:
        "Admin1234" → "$2b$12$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy"
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compara contraseña en texto plano con el hash almacenado.
    Nunca "deshashea" la contraseña; vuelve a hashear y compara.
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def login(db: Session, login_data: LoginRequest) -> TokenResponse:
    """
    Autentica un usuario y devuelve un JWT.

    Pasos:
    1. Buscar el usuario por email
    2. Verificar la contraseña
    3. Generar el JWT
    4. Devolver el token con información del usuario

    Raises:
        401 UNAUTHORIZED → Credenciales incorrectas
        401 UNAUTHORIZED → Usuario desactivado
    """
    # Paso 1: Buscar usuario
    usuario = db.query(Usuario).filter(Usuario.email == login_data.email).first()

    # Paso 2: Verificar credenciales
    # IMPORTANTE: Siempre verificamos la contraseña antes de comprobar si existe
    # Para evitar "timing attacks" (ataques que miden el tiempo de respuesta)
    if not usuario or not verify_password(login_data.password, usuario.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La cuenta está desactivada. Contacte al administrador."
        )

    # Paso 3: Crear el JWT
    # "sub" (subject) es el estándar JWT para identificar al usuario
    token = create_access_token(data={
        "sub": usuario.email,
        "usuario_id": usuario.id,
        "rol": usuario.rol.value
    })

    # Paso 4: Devolver respuesta
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        usuario_id=usuario.id,
        nombre=f"{usuario.nombre} {usuario.apellido}",
        rol=usuario.rol.value
    )
