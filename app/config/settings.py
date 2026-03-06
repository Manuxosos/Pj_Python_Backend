"""
CONFIGURACIÓN DE LA APLICACIÓN
================================
Similar al application.properties de Spring Boot.

Pydantic BaseSettings lee automáticamente las variables de entorno
y del archivo .env. Es type-safe (con tipos de datos verificados).

CONCEPTOS CLAVE:
- Settings como clase = configuración centralizada y tipada
- lru_cache = la configuración se crea UNA sola vez (patrón Singleton)
- Pydantic valida los tipos automáticamente
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Configuración central de la aplicación.
    Equivale al application.properties de Spring Boot.
    """

    # --- Información de la app ---
    app_name: str = "ShopFlow API"
    app_version: str = "1.0.0"
    debug: bool = True

    # --- Base de datos ---
    # SQLite para desarrollo, PostgreSQL para producción
    database_url: str = "sqlite:///./shopflow.db"

    # --- JWT (JSON Web Tokens) ---
    # secret_key: clave para firmar los tokens (como un sello digital)
    secret_key: str = "clave-super-secreta-cambiar-en-produccion-12345"
    algorithm: str = "HS256"  # Algoritmo de firma
    access_token_expire_minutes: int = 30  # El token expira en 30 minutos

    class Config:
        # Lee variables desde el archivo .env
        env_file = ".env"
        # Permite sobreescribir con variables de entorno del sistema
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna la configuración como Singleton.
    lru_cache garantiza que se crea solo UNA instancia.

    Uso en otros archivos:
        from app.config.settings import get_settings
        settings = get_settings()
        print(settings.app_name)
    """
    return Settings()
