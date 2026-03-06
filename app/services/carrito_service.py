"""
SERVICIO DE CARRITO
====================
La lógica de negocio del carrito de compra.

OPERACIONES PRINCIPALES:
  1. Ver carrito del usuario actual
  2. Añadir producto (verificar stock)
  3. Actualizar cantidad (verificar stock)
  4. Quitar un producto
  5. Vaciar carrito

REGLAS DE NEGOCIO (lógica que no está en el modelo):
  - No se puede añadir más unidades que el stock disponible
  - Si el producto ya está en el carrito, se suma la cantidad
  - El stock no se reserva al añadir al carrito (solo al confirmar pedido)
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.carrito import Carrito, CarritoItem
from app.models.producto import Producto
from app.models.usuario import Usuario


def get_carrito(db: Session, usuario: Usuario) -> Carrito:
    """
    Obtiene el carrito del usuario.
    Si por alguna razón no existe, lo crea (caso de usuarios migrados).
    """
    carrito = db.query(Carrito).filter(Carrito.usuario_id == usuario.id).first()
    if not carrito:
        carrito = Carrito(usuario_id=usuario.id)
        db.add(carrito)
        db.commit()
        db.refresh(carrito)
    return carrito


def _get_producto(db: Session, producto_id: int) -> Producto:
    """Busca un producto activo. Lanza 404 si no existe."""
    producto = db.query(Producto).filter(
        Producto.id == producto_id,
        Producto.activo == True
    ).first()
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {producto_id} no encontrado"
        )
    return producto


def anadir_item(
    db: Session,
    usuario: Usuario,
    producto_id: int,
    cantidad: int
) -> Carrito:
    """
    Añade un producto al carrito o incrementa su cantidad.

    Reglas:
    - Si el producto ya está en el carrito → suma la cantidad
    - Si no está → crea un nuevo CarritoItem
    - No puede exceder el stock disponible

    Returns:
        El carrito actualizado
    """
    carrito = get_carrito(db, usuario)
    producto = _get_producto(db, producto_id)

    # Verificar stock
    if producto.stock < cantidad:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock insuficiente. Disponibles: {producto.stock} unidades"
        )

    # Ver si el producto ya está en el carrito
    item_existente = db.query(CarritoItem).filter(
        CarritoItem.carrito_id == carrito.id,
        CarritoItem.producto_id == producto_id
    ).first()

    if item_existente:
        # Sumar cantidad pero sin pasar del stock
        nueva_cantidad = item_existente.cantidad + cantidad
        if nueva_cantidad > producto.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock insuficiente. Ya tienes {item_existente.cantidad} en el carrito. "
                       f"Stock disponible: {producto.stock}"
            )
        item_existente.cantidad = nueva_cantidad
    else:
        # Nuevo item
        nuevo_item = CarritoItem(
            carrito_id=carrito.id,
            producto_id=producto_id,
            cantidad=cantidad
        )
        db.add(nuevo_item)

    db.commit()
    db.refresh(carrito)
    return carrito


def actualizar_cantidad(
    db: Session,
    usuario: Usuario,
    producto_id: int,
    cantidad: int
) -> Carrito:
    """Cambia la cantidad de un producto en el carrito."""
    carrito = get_carrito(db, usuario)
    producto = _get_producto(db, producto_id)

    item = db.query(CarritoItem).filter(
        CarritoItem.carrito_id == carrito.id,
        CarritoItem.producto_id == producto_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado en el carrito"
        )

    if cantidad > producto.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock insuficiente. Disponibles: {producto.stock} unidades"
        )

    item.cantidad = cantidad
    db.commit()
    db.refresh(carrito)
    return carrito


def quitar_item(db: Session, usuario: Usuario, producto_id: int) -> Carrito:
    """Quita un producto del carrito."""
    carrito = get_carrito(db, usuario)

    item = db.query(CarritoItem).filter(
        CarritoItem.carrito_id == carrito.id,
        CarritoItem.producto_id == producto_id
    ).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado en el carrito"
        )

    db.delete(item)
    db.commit()
    db.refresh(carrito)
    return carrito


def vaciar(db: Session, usuario: Usuario) -> Carrito:
    """Elimina todos los items del carrito."""
    carrito = get_carrito(db, usuario)
    for item in carrito.items:
        db.delete(item)
    db.commit()
    db.refresh(carrito)
    return carrito
