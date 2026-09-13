from datetime import datetime
from typing import Optional
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.auth import get_current_user
from app.models import InventoryTransaction, Product, User

router = APIRouter(prefix="/inventory", tags=["inventory"])


class TransactionType(str, Enum):
    inbound = "inbound"
    outbound = "outbound"
    adjustment = "adjustment"


class TransactionCreate(BaseModel):
    product_id: int
    transaction_type: TransactionType
    quantity: int
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    product_id: int
    transaction_type: str
    quantity: int
    reference_number: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class InventorySummary(BaseModel):
    product_id: int
    product_name: str
    current_stock: int
    minimum_stock: int
    total_inbound: int
    total_outbound: int
    net_movement: int


class AdjustStock(BaseModel):
    new_stock: int
    notes: Optional[str] = None


@router.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def add_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == transaction.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if transaction.transaction_type == TransactionType.outbound and product.current_stock < transaction.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    if transaction.transaction_type == TransactionType.inbound:
        product.current_stock += transaction.quantity
    elif transaction.transaction_type == TransactionType.outbound:
        product.current_stock -= transaction.quantity
    elif transaction.transaction_type == TransactionType.adjustment:
        product.current_stock = transaction.quantity

    db_transaction = InventoryTransaction(
        product_id=transaction.product_id,
        transaction_type=transaction.transaction_type.value,
        quantity=transaction.quantity,
        reference_number=transaction.reference_number,
        notes=transaction.notes,
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.get("/transactions", response_model=list[TransactionResponse])
def get_transaction_history(
    product_id: Optional[int] = None,
    transaction_type: Optional[TransactionType] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(InventoryTransaction)
    if product_id:
        query = query.filter(InventoryTransaction.product_id == product_id)
    if transaction_type:
        query = query.filter(InventoryTransaction.transaction_type == transaction_type.value)
    return query.order_by(InventoryTransaction.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/summary", response_model=list[InventorySummary])
def get_inventory_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    products = db.query(Product).all()
    summaries = []
    for product in products:
        inbound = db.query(InventoryTransaction).filter(
            InventoryTransaction.product_id == product.id,
            InventoryTransaction.transaction_type == "inbound",
        ).with_entities(InventoryTransaction.quantity).all()
        outbound = db.query(InventoryTransaction).filter(
            InventoryTransaction.product_id == product.id,
            InventoryTransaction.transaction_type == "outbound",
        ).with_entities(InventoryTransaction.quantity).all()

        total_inbound = sum(t.quantity for t in inbound)
        total_outbound = sum(t.quantity for t in outbound)

        summaries.append(InventorySummary(
            product_id=product.id,
            product_name=product.name,
            current_stock=product.current_stock,
            minimum_stock=product.minimum_stock,
            total_inbound=total_inbound,
            total_outbound=total_outbound,
            net_movement=total_inbound - total_outbound,
        ))
    return summaries


@router.put("/adjust/{product_id}", response_model=TransactionResponse)
def adjust_stock(
    product_id: int,
    adjustment: AdjustStock,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    old_stock = product.current_stock
    product.current_stock = adjustment.new_stock

    db_transaction = InventoryTransaction(
        product_id=product_id,
        transaction_type="adjustment",
        quantity=abs(adjustment.new_stock - old_stock),
        notes=adjustment.notes or f"Stock adjusted from {old_stock} to {adjustment.new_stock}",
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction
