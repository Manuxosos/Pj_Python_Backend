"""
SCHEMAS DE USUARIO
===================
Tres tipos de schemas por entidad (patrón estándar):

  1. UsuarioCreate → datos para CREAR un usuario (input)
  2. UsuarioUpdate → datos para ACTUALIZAR (campos opcionales)
  3. UsuarioResponse → datos que se DEVUELVEN al cliente (output)

¿Por qué separar input de output?
  - No devolvemos la contraseña nunca
  - No aceptamos el rol desde el cliente en creación
  - Control total sobre qué se expone en la API

Equivale a los DTOs de Java:
  UsuarioCreate   → CreateUsuarioDTO
  UsuarioUpdate   → UpdateUsuarioDTO
  UsuarioResponse → UsuarioResponseDTO
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.usuario import RolUsuario


# ==============================================================
# SCHEMA DE CREACIÓN (INPUT)
# ==============================================================
class UsuarioCreate(BaseModel):
    """
    Datos necesarios para registrar un nuevo usuario.
    La contraseña se hasheará en el service antes de guardar.
    """
    email: EmailStr = Field(
        ...,
        example="juan@empresa.com",
        description="Email único del usuario"
    )
    nombre: str = Field(
        ...,
        min_length=2,
        max_length=100,
        example="Juan García",
        description="Nombre completo"
    )
    password: str = Field(
        ...,
        min_length=8,
        example="MiPassword123",
        description="Mínimo 8 caracteres"
    )
    rol: RolUsuario = Field(
        default=RolUsuario.DESARROLLADOR,
        description="Rol en el sistema"
    )

    # Validador personalizado (como @Pattern en Bean Validation de Java)
    @field_validator("password")
    @classmethod
    def password_must_have_digit(cls, v: str) -> str:
        """La contraseña debe contener al menos un número."""
        if not any(char.isdigit() for char in v):
            raise ValueError("La contraseña debe contener al menos un número")
        return v


# ==============================================================
# SCHEMA DE ACTUALIZACIÓN (INPUT)
# ==============================================================
class UsuarioUpdate(BaseModel):
    """
    Datos para actualizar un usuario.
    Todos los campos son OPCIONALES (None = no cambiar).
    """
    nombre: str | None = Field(None, min_length=2, max_length=100)
    password: str | None = Field(None, min_length=8)
    activo: bool | None = None


# ==============================================================
# SCHEMA DE RESPUESTA (OUTPUT)
# ==============================================================
class UsuarioResponse(BaseModel):
    """
    Datos que se devuelven al cliente.
    NUNCA incluye la contraseña.
    """
    id: int
    email: str
    nombre: str
    rol: RolUsuario
    activo: bool
    created_at: datetime

    # model_config reemplaza a 'class Config' de Pydantic v1
    # from_attributes=True permite crear el schema desde un objeto SQLAlchemy
    # Equivale a @JsonProperty en Jackson (Java)
    model_config = {"from_attributes": True}


class UsuarioResumenResponse(BaseModel):
    """
    Versión reducida del usuario (para incluir en otras respuestas).
    Por ejemplo: al mostrar quién creó una tarea.
    """
    id: int
    nombre: str
    email: str
    rol: RolUsuario

    model_config = {"from_attributes": True}
