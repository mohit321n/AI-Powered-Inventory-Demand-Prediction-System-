from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Product, Transaction, TransactionType


def add_transaction(db: Session, transaction_data: dict, product_id: int) -> Transaction:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    transaction = Transaction(product_id=product_id, **transaction_data)

    if transaction.transaction_type == TransactionType.IN:
        product.current_stock += transaction.quantity
    elif transaction.transaction_type == TransactionType.OUT:
        if product.current_stock < transaction.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock"
            )
        product.current_stock -= transaction.quantity
    elif transaction.transaction_type == TransactionType.ADJUSTMENT:
        product.current_stock = transaction.quantity

    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def get_inventory_history(
    db: Session,
    product_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Transaction]:
    query = db.query(Transaction).filter(Transaction.product_id == product_id)
    if start_date:
        query = query.filter(Transaction.created_at >= start_date)
    if end_date:
        query = query.filter(Transaction.created_at <= end_date)
    return query.order_by(Transaction.created_at.desc()).all()


def get_inventory_summary(db: Session) -> List[dict]:
    products = db.query(Product).all()
    return [
        {
            "product_id": p.id,
            "product_name": p.name,
            "current_stock": p.current_stock,
            "minimum_stock": p.minimum_stock,
            "maximum_stock": p.maximum_stock,
            "status": "low" if p.current_stock <= p.minimum_stock else "ok"
        }
        for p in products
    ]


def adjust_stock(db: Session, product_id: int, new_quantity: int, reason: str) -> Transaction:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    old_quantity = product.current_stock
    difference = new_quantity - old_quantity

    product.current_stock = new_quantity
    transaction = Transaction(
        product_id=product_id,
        transaction_type=TransactionType.ADJUSTMENT,
        quantity=abs(difference),
        notes=reason
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def check_low_stock(db: Session) -> List[Product]:
    return db.query(Product).filter(
        Product.current_stock <= Product.minimum_stock
    ).all()
