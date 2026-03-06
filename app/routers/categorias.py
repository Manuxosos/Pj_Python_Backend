"""
ROUTER DE CATEGORÍAS
======================
Las categorías son PÚBLICAS para lectura.
Solo ADMIN puede crear/editar/borrar.

El frontend usa las categorías para:
  - Menú de navegación de la tienda
  - Filtros en el listado de productos
  - Breadcrumbs en la página de producto
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.usuario import Usuario
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate, CategoriaResponse
from app.security.dependencies import require_admin
from app.services import categoria_service

router = APIRouter(prefix="/api/categorias", tags=["📂 Categorías"])


@router.get("/", response_model=list[CategoriaResponse], summary="Listar categorías")
def listar_categorias(db: Session = Depends(get_db)):
    """
    PÚBLICO (sin autenticación).
    El frontend carga este endpoint al iniciar para construir el menú de navegación.
    """
    categorias = categoria_service.get_all(db)
    return [
        CategoriaResponse(
            id=c.id,
            nombre=c.nombre,
            descripcion=c.descripcion,
            icono=c.icono,
            activo=c.activo,
            total_productos=len([p for p in c.productos if p.activo])
        )
        for c in categorias
    ]


@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED,
             summary="Crear categoría")
def crear_categoria(datos: CategoriaCreate, db: Session = Depends(get_db),
                    _admin: Usuario = Depends(require_admin)):
    """Solo ADMIN puede crear categorías."""
    cat = categoria_service.create(db, datos)
    return CategoriaResponse(
        id=cat.id, nombre=cat.nombre, descripcion=cat.descripcion,
        icono=cat.icono, activo=cat.activo, total_productos=0
    )


@router.get("/{categoria_id}", response_model=CategoriaResponse, summary="Ver categoría")
def ver_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """PÚBLICO."""
    cat = categoria_service.get_by_id(db, categoria_id)
    return CategoriaResponse(
        id=cat.id, nombre=cat.nombre, descripcion=cat.descripcion,
        icono=cat.icono, activo=cat.activo,
        total_productos=len([p for p in cat.productos if p.activo])
    )


@router.put("/{categoria_id}", response_model=CategoriaResponse, summary="Actualizar categoría")
def actualizar_categoria(categoria_id: int, datos: CategoriaUpdate,
                         db: Session = Depends(get_db),
                         _admin: Usuario = Depends(require_admin)):
    cat = categoria_service.update(db, categoria_id, datos)
    return CategoriaResponse(
        id=cat.id, nombre=cat.nombre, descripcion=cat.descripcion,
        icono=cat.icono, activo=cat.activo,
        total_productos=len([p for p in cat.productos if p.activo])
    )


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Eliminar categoría")
def eliminar_categoria(categoria_id: int, db: Session = Depends(get_db),
                       _admin: Usuario = Depends(require_admin)):
    categoria_service.delete(db, categoria_id)
