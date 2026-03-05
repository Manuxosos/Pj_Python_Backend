"""
SCHEMAS DE AUTENTICACIÓN
==========================
Pydantic schemas para el proceso de login y tokens JWT.

Pydantic en Python equivale a:
  - Clases DTO (Data Transfer Objects) de Java
  - Bean Validation (@NotNull, @Size, @Email)
  - Jackson (serialización/deserialización JSON)

Los schemas:
  - Validan los datos de entrada automáticamente
  - Serializan la respuesta a JSON
  - Generan la documentación Swagger automáticamente
  - Son INMUTABLES (como Records en Java 16+)
"""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """
    Datos requeridos para hacer login.
    Equivale a LoginRequestDTO en Java.

    Field() permite agregar validaciones y metadatos:
      - min_length, max_length: longitud de strings
      - example: valor de ejemplo en Swagger
    """
    email: EmailStr = Field(
        ...,  # ... significa REQUERIDO (equivale a @NotNull en Java)
        example="admin@taskflow.com",
        description="Email del usuario registrado"
    )
    password: str = Field(
        ...,
        min_length=6,
        example="Admin1234",
        description="Contraseña del usuario"
    )


class TokenResponse(BaseModel):
    """
    Respuesta del endpoint de login con el JWT.
    Equivale a TokenResponseDTO en Java.
    """
    access_token: str = Field(description="JWT Token para usar en las peticiones")
    token_type: str = Field(default="bearer", description="Tipo de token (siempre 'bearer')")
    expires_in: int = Field(description="Segundos hasta que expire el token")
    usuario_id: int = Field(description="ID del usuario autenticado")
    nombre: str = Field(description="Nombre del usuario autenticado")
    rol: str = Field(description="Rol del usuario (ADMIN, MANAGER, DESARROLLADOR)")


class TokenData(BaseModel):
    """
    Datos contenidos dentro del JWT (payload).
    Se usa internamente para verificar tokens.
    """
    email: str | None = None
    usuario_id: int | None = None
    rol: str | None = None
