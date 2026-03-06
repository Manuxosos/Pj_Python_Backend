"""
SCHEMAS DE USUARIO
===================
Tres schemas por entidad (patrón estándar en APIs REST):

  1. UsuarioCreate   → datos para CREAR (input del cliente)
  2. UsuarioUpdate   → datos para ACTUALIZAR (todos opcionales)
  3. UsuarioResponse → datos que DEVOLVEMOS (nunca la contraseña)

Registro público vs creación de admin:
  - Cualquiera puede registrarse → rol siempre CLIENTE
  - Solo ADMIN puede crear otros ADMIN
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.usuario import RolUsuario


class UsuarioRegistro(BaseModel):
    """
    Registro público: cualquier persona puede crear una cuenta.
    El rol siempre será CLIENTE (el frontend no puede elegir ser ADMIN).
    """
    email: EmailStr = Field(..., example="maria@email.com")
    nombre: str = Field(..., min_length=2, max_length=100, example="María")
    apellido: str = Field(..., min_length=2, max_length=100, example="González")
    password: str = Field(..., min_length=8, example="MiPassword123")

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Contraseña debe tener al menos un número."""
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe contener al menos un número")
        return v


class UsuarioCreate(BaseModel):
    """Creación por admin (puede asignar cualquier rol)."""
    email: EmailStr = Field(..., example="nuevo.admin@shopflow.com")
    nombre: str = Field(..., min_length=2, max_length=100, example="Nuevo")
    apellido: str = Field(..., min_length=2, max_length=100, example="Admin")
    password: str = Field(..., min_length=8, example="Admin5678")
    rol: RolUsuario = Field(default=RolUsuario.CLIENTE)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe contener al menos un número")
        return v


class UsuarioUpdate(BaseModel):
    """Actualización de perfil (todos los campos opcionales)."""
    nombre: str | None = Field(None, min_length=2, max_length=100)
    apellido: str | None = Field(None, min_length=2, max_length=100)
    password: str | None = Field(None, min_length=8)


class UsuarioResponse(BaseModel):
    """Respuesta pública de usuario. NUNCA incluye la contraseña."""
    id: int
    email: str
    nombre: str
    apellido: str
    rol: RolUsuario
    activo: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UsuarioResumenResponse(BaseModel):
    """Versión mínima para incluir en otras respuestas (pedidos, etc.)."""
    id: int
    nombre: str
    apellido: str
    email: str

    model_config = {"from_attributes": True}
