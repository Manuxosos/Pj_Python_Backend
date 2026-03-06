"""
ROUTER DE CARRITO
==================
Gestión del carrito de compra del usuario autenticado.

DISEÑO REST del carrito:
  GET    /api/carrito/                      → Ver mi carrito
  POST   /api/carrito/items                 → Añadir producto
  PUT    /api/carrito/items/{producto_id}   → Cambiar cantidad
  DELETE /api/carrito/items/{producto_id}   → Quitar producto
  DELETE /api/carrito/                      → Vaciar carrito

FLUJO TÍPICO DEL FRONTEND:
  1. Usuario ve producto: botón "Añadir al carrito"
  2. Frontend: POST /api/carrito/items {"producto_id": 5, "cantidad": 1}
  3. Backend actualiza BD, devuelve carrito actualizado
  4. Frontend actualiza el badge del carrito en el header: "🛒 (3)"
  5. Usuario va al carrito: GET /api/carrito/
  6. Frontend muestra items con totales
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.usuario import Usuario
from app.schemas.carrito import (
    AnadirItemRequest, ActualizarCantidadRequest, CarritoResponse, CarritoItemResponse
)
from app.security.dependencies import get_usuario_actual
from app.services import carrito_service

router = APIRouter(prefix="/api/carrito", tags=["🛒 Carrito"])


def _carrito_to_response(carrito) -> CarritoResponse:
    """Construye la respuesta del carrito con campos calculados."""
    items = [
        CarritoItemResponse(
            id=item.id,
            producto={
                "id": item.producto.id,
                "nombre": item.producto.nombre,
                "precio_final": item.producto.precio_final,
                "tiene_descuento": item.producto.tiene_descuento,
                "imagen_url": item.producto.imagen_url,
                "stock": item.producto.stock,
                "disponible": item.producto.stock > 0
            },
            cantidad=item.cantidad,
            subtotal=item.subtotal
        )
        for item in carrito.items
    ]
    return CarritoResponse(
        id=carrito.id,
        items=items,
        total=round(carrito.total, 2),
        total_items=carrito.total_items
    )


@router.get("/", response_model=CarritoResponse, summary="Ver mi carrito")
def ver_carrito(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """
    Devuelve el carrito completo con todos los items y el total.
    El frontend llama esto al abrir la página del carrito.
    """
    carrito = carrito_service.get_carrito(db, usuario)
    return _carrito_to_response(carrito)


@router.post(
    "/items",
    response_model=CarritoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Añadir producto al carrito"
)
def anadir_item(
    datos: AnadirItemRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """
    Añade un producto al carrito.
    Si ya está, suma la cantidad.
    Verifica que hay suficiente stock.
    """
    carrito = carrito_service.anadir_item(db, usuario, datos.producto_id, datos.cantidad)
    return _carrito_to_response(carrito)


@router.put(
    "/items/{producto_id}",
    response_model=CarritoResponse,
    summary="Cambiar cantidad"
)
def actualizar_cantidad(
    producto_id: int,
    datos: ActualizarCantidadRequest,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """
    Cambia la cantidad de un producto en el carrito.
    El frontend llama esto cuando el usuario usa +/- en la cantidad.
    """
    carrito = carrito_service.actualizar_cantidad(db, usuario, producto_id, datos.cantidad)
    return _carrito_to_response(carrito)


@router.delete(
    "/items/{producto_id}",
    response_model=CarritoResponse,
    summary="Quitar producto del carrito"
)
def quitar_item(
    producto_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Elimina un producto del carrito."""
    carrito = carrito_service.quitar_item(db, usuario, producto_id)
    return _carrito_to_response(carrito)


@router.delete("/", response_model=CarritoResponse, summary="Vaciar carrito")
def vaciar_carrito(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_usuario_actual)
):
    """Elimina todos los items del carrito."""
    carrito = carrito_service.vaciar(db, usuario)
    return _carrito_to_response(carrito)
