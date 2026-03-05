"""
MANEJADORES DE EXCEPCIONES GLOBALES
=====================================
Equivale al @RestControllerAdvice / @ExceptionHandler de Spring Boot.

Captura errores de toda la aplicación y los convierte en
respuestas JSON con el formato correcto.

Sin esto, un error 422 de validación de Pydantic devuelve
un JSON muy técnico. Con el handler, lo formateamos bonito.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError


def registrar_handlers(app: FastAPI) -> None:
    """
    Registra todos los manejadores de errores en la app FastAPI.
    Se llama desde main.py.
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ) -> JSONResponse:
        """
        Maneja errores de validación de Pydantic (422 Unprocessable Entity).
        Formatea los errores de forma legible.

        Equivale a @ExceptionHandler(MethodArgumentNotValidException.class)
        en Spring Boot.
        """
        errores = []
        for error in exc.errors():
            campo = " → ".join(str(loc) for loc in error["loc"] if loc != "body")
            errores.append({
                "campo": campo,
                "mensaje": error["msg"],
                "tipo": error["type"]
            })

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Error de validación",
                "detalle": errores
            }
        )

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(
        request: Request,
        exc: IntegrityError
    ) -> JSONResponse:
        """
        Maneja errores de integridad de la BD (duplicados, FK violadas).
        Equivale a @ExceptionHandler(DataIntegrityViolationException.class).
        """
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "Conflicto de datos",
                "detalle": "Ya existe un registro con esos datos únicos"
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """
        Catch-all para errores no manejados.
        Evita que se filtren detalles internos al cliente.
        """
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Error interno del servidor",
                "detalle": "Ha ocurrido un error inesperado. Por favor, contacte al soporte."
            }
        )
