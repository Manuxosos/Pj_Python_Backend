"""
SERVICIO DE PRODUCTOS
======================
Incluye búsqueda y filtrado avanzado del catálogo.

El endpoint de catálogo es el más importante del e-commerce.
El frontend lo usa para:
  - Página de inicio (productos destacados)
  - Listado por categoría
  - Buscador de la tienda
  - Filtros de precio
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from app.models.producto import Producto
from app.schemas.producto import ProductoCreate, ProductoUpdate, ProductoResponse


def _build_response(producto: Producto) -> ProductoResponse:
    """Construye ProductoResponse con campos calculados."""
    precio_final = producto.precio_descuento if producto.precio_descuento else producto.precio
    tiene_descuento = producto.precio_descuento is not None and producto.precio_descuento < producto.precio

    if tiene_descuento:
        porcentaje = round((1 - producto.precio_descuento / producto.precio) * 100, 1)
    else:
        porcentaje = 0.0

    return ProductoResponse(
        id=producto.id,
        nombre=producto.nombre,
        descripcion=producto.descripcion,
        precio=producto.precio,
        precio_descuento=producto.precio_descuento,
        precio_final=precio_final,
        tiene_descuento=tiene_descuento,
        porcentaje_descuento=porcentaje,
        stock=producto.stock,
        disponible=producto.stock > 0,
        imagen_url=producto.imagen_url,
        destacado=producto.destacado,
        categoria_id=producto.categoria_id,
        categoria_nombre=producto.categoria.nombre if producto.categoria else "Sin categoría",
        created_at=producto.created_at,
    )


def get_catalogo(
    db: Session,
    categoria_id: int | None = None,
    busqueda: str | None = None,
    min_precio: float | None = None,
    max_precio: float | None = None,
    solo_disponibles: bool = False,
    solo_destacados: bool = False,
    orden: str = "nombre_asc"
) -> list[ProductoResponse]:
    """
    Catálogo con filtros. PÚBLICO (sin autenticación).

    Filtros disponibles (query params para el frontend):
      categoria_id     → filtrar por categoría
      busqueda         → buscar en nombre y descripción
      min_precio       → precio mínimo
      max_precio       → precio máximo
      solo_disponibles → solo productos con stock > 0
      solo_destacados  → solo productos destacados (para el home)
      orden            → nombre_asc, nombre_desc, precio_asc, precio_desc

    Ejemplo de URL del frontend:
      /api/productos/?categoria_id=1&busqueda=laptop&max_precio=2000&orden=precio_asc
    """
    query = db.query(Producto).filter(Producto.activo == True)

    # Filtrar por categoría
    if categoria_id:
        query = query.filter(Producto.categoria_id == categoria_id)

    # Búsqueda por texto (en nombre O descripción)
    if busqueda:
        termino = f"%{busqueda}%"
        query = query.filter(
            or_(
                Producto.nombre.ilike(termino),      # ilike = case-insensitive LIKE
                Producto.descripcion.ilike(termino)
            )
        )

    # Filtros de precio
    if min_precio is not None:
        query = query.filter(Producto.precio >= min_precio)
    if max_precio is not None:
        query = query.filter(Producto.precio <= max_precio)

    # Solo disponibles (stock > 0)
    if solo_disponibles:
        query = query.filter(Producto.stock > 0)

    # Solo destacados
    if solo_destacados:
        query = query.filter(Producto.destacado == True)

    # Ordenación
    orden_map = {
        "nombre_asc": Producto.nombre.asc(),
        "nombre_desc": Producto.nombre.desc(),
        "precio_asc": Producto.precio.asc(),
        "precio_desc": Producto.precio.desc(),
    }
    query = query.order_by(orden_map.get(orden, Producto.nombre.asc()))

    productos = query.all()
    return [_build_response(p) for p in productos]


def get_by_id(db: Session, producto_id: int) -> Producto:
    """Busca un producto. Lanza 404 si no existe."""
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


def create(db: Session, datos: ProductoCreate) -> Producto:
    """Crea un nuevo producto. Solo ADMIN."""
    # Verificar que la categoría existe
    from app.models.categoria import Categoria
    categoria = db.query(Categoria).filter(Categoria.id == datos.categoria_id).first()
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con ID {datos.categoria_id} no encontrada"
        )

    producto = Producto(**datos.model_dump())
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto


def update(db: Session, producto_id: int, datos: ProductoUpdate) -> Producto:
    """Actualiza producto. Solo ADMIN."""
    producto = get_by_id(db, producto_id)
    for field, value in datos.model_dump(exclude_none=True).items():
        setattr(producto, field, value)
    db.commit()
    db.refresh(producto)
    return producto


def delete(db: Session, producto_id: int) -> None:
    """Soft delete de producto. Solo ADMIN."""
    producto = get_by_id(db, producto_id)
    producto.activo = False
    db.commit()
