"""SERVICIO DE CATEGORÍAS"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate


def get_all(db: Session, solo_activas: bool = True) -> list[Categoria]:
    query = db.query(Categoria)
    if solo_activas:
        query = query.filter(Categoria.activo == True)
    return query.order_by(Categoria.nombre).all()


def get_by_id(db: Session, categoria_id: int) -> Categoria:
    cat = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con ID {categoria_id} no encontrada"
        )
    return cat


def create(db: Session, datos: CategoriaCreate) -> Categoria:
    existe = db.query(Categoria).filter(Categoria.nombre == datos.nombre).first()
    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una categoría con el nombre '{datos.nombre}'"
        )
    categoria = Categoria(**datos.model_dump())
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


def update(db: Session, categoria_id: int, datos: CategoriaUpdate) -> Categoria:
    categoria = get_by_id(db, categoria_id)
    for field, value in datos.model_dump(exclude_none=True).items():
        setattr(categoria, field, value)
    db.commit()
    db.refresh(categoria)
    return categoria


def delete(db: Session, categoria_id: int) -> None:
    """Soft delete. No borra si tiene productos activos."""
    categoria = get_by_id(db, categoria_id)
    productos_activos = sum(1 for p in categoria.productos if p.activo)
    if productos_activos > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar: la categoría tiene {productos_activos} productos activos"
        )
    categoria.activo = False
    db.commit()
