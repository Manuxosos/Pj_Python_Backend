"""
ROUTER DE PRODUCTOS
====================
El catálogo es PÚBLICO. La gestión (CRUD) solo para ADMIN.

QUERY PARAMETERS para el frontend:
  GET /api/productos/?categoria_id=1&busqueda=iphone&min_precio=500&orden=precio_asc

Así el frontend puede construir:
  - Buscador: ?busqueda=texto
  - Filtro de categoría: ?categoria_id=2
  - Rango de precio: ?min_precio=100&max_precio=1000
  - Ordenación: ?orden=precio_asc | precio_desc | nombre_asc
  - Solo en oferta: productos con precio_descuento
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.usuario import Usuario
from app.schemas.producto import ProductoCreate, ProductoUpdate, ProductoResponse
from app.security.dependencies import require_admin
from app.services import producto_service

router = APIRouter(prefix="/api/productos", tags=["🛍️ Productos"])


@router.get(
    "/",
    response_model=list[ProductoResponse],
    summary="Catálogo de productos",
    description="""
**PÚBLICO** — Sin autenticación.

Filtra el catálogo con query parameters:
- `categoria_id` → Filtrar por categoría
- `busqueda` → Buscar en nombre y descripción
- `min_precio` / `max_precio` → Rango de precio
- `solo_disponibles` → Solo productos con stock
- `solo_destacados` → Solo productos del home
- `orden` → `nombre_asc`, `nombre_desc`, `precio_asc`, `precio_desc`
    """
)
def catalogo(
    db: Session = Depends(get_db),
    # Query() define parámetros opcionales de URL
    # El frontend los envía así: /api/productos/?categoria_id=1&busqueda=laptop
    categoria_id: int | None = Query(None, description="ID de categoría"),
    busqueda: str | None = Query(None, description="Texto a buscar"),
    min_precio: float | None = Query(None, ge=0, description="Precio mínimo"),
    max_precio: float | None = Query(None, gt=0, description="Precio máximo"),
    solo_disponibles: bool = Query(False, description="Solo con stock"),
    solo_destacados: bool = Query(False, description="Solo destacados"),
    orden: str = Query("nombre_asc", description="Ordenar por: nombre_asc, precio_asc, precio_desc")
):
    """
    El endpoint más llamado de la tienda.
    El frontend lo usa para mostrar el catálogo con filtros en tiempo real.
    """
    return producto_service.get_catalogo(
        db, categoria_id, busqueda, min_precio, max_precio,
        solo_disponibles, solo_destacados, orden
    )


@router.get("/{producto_id}", response_model=ProductoResponse, summary="Ver producto")
def ver_producto(producto_id: int, db: Session = Depends(get_db)):
    """PÚBLICO. Página de detalle de producto del frontend."""
    producto = producto_service.get_by_id(db, producto_id)
    return producto_service._build_response(producto)


@router.post("/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED,
             summary="Crear producto")
def crear_producto(datos: ProductoCreate, db: Session = Depends(get_db),
                   _admin: Usuario = Depends(require_admin)):
    """Solo ADMIN puede añadir productos al catálogo."""
    producto = producto_service.create(db, datos)
    return producto_service._build_response(producto)


@router.put("/{producto_id}", response_model=ProductoResponse, summary="Actualizar producto")
def actualizar_producto(producto_id: int, datos: ProductoUpdate,
                        db: Session = Depends(get_db),
                        _admin: Usuario = Depends(require_admin)):
    """Solo ADMIN. Actualizar precio, stock, descripción, etc."""
    producto = producto_service.update(db, producto_id, datos)
    return producto_service._build_response(producto)


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Eliminar producto")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db),
                      _admin: Usuario = Depends(require_admin)):
    """Soft delete. El producto deja de aparecer en el catálogo."""
    producto_service.delete(db, producto_id)
