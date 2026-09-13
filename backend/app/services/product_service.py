from typing import Optional, List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Product, Category, Supplier
from app.schemas import ProductCreate, CategoryCreate, SupplierCreate


def create_product(db: Session, product_data: ProductCreate) -> Product:
    product = Product(**product_data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_product(db: Session, product_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def list_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    search: Optional[str] = None
) -> List[Product]:
    query = db.query(Product)
    if category:
        query = query.join(Category).filter(Category.name == category)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    return query.offset(skip).limit(limit).all()


def update_product(db: Session, product_id: int, product_data: dict) -> Product:
    product = get_product(db, product_id)
    for key, value in product_data.items():
        if value is not None:
            setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int) -> None:
    product = get_product(db, product_id)
    db.delete(product)
    db.commit()


def create_category(db: Session, category_data: CategoryCreate) -> Category:
    category = Category(**category_data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def list_categories(db: Session) -> List[Category]:
    return db.query(Category).all()


def create_supplier(db: Session, supplier_data: SupplierCreate) -> Supplier:
    supplier = Supplier(**supplier_data.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


def list_suppliers(db: Session) -> List[Supplier]:
    return db.query(Supplier).all()
