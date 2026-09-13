import csv
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Sale, Product, Transaction, TransactionType


def add_sale(db: Session, sale_data: dict) -> Sale:
    product = db.query(Product).filter(Product.id == sale_data["product_id"]).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if product.current_stock < sale_data["quantity"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stock")

    product.current_stock -= sale_data["quantity"]

    sale = Sale(**sale_data)
    transaction = Transaction(
        product_id=sale_data["product_id"],
        transaction_type=TransactionType.OUT,
        quantity=sale_data["quantity"],
        notes="Sale"
    )
    db.add(sale)
    db.add(transaction)
    db.commit()
    db.refresh(sale)
    return sale


def upload_csv(db: Session, file_path: str, user_id: int) -> dict:
    success_count = 0
    error_count = 0
    errors = []

    with open(file_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                product = db.query(Product).filter(Product.name == row["product_name"]).first()
                if not product:
                    product = Product(name=row["product_name"], sku=row.get("sku", ""))
                    db.add(product)
                    db.flush()

                quantity = int(row["quantity"])
                price = float(row["price"])
                product.current_stock -= quantity

                sale = Sale(
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=price,
                    total_amount=quantity * price,
                    sale_date=datetime.strptime(row["date"], "%Y-%m-%d"),
                    user_id=user_id
                )
                db.add(sale)
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(str(e))

    db.commit()
    return {"success": success_count, "errors": error_count, "error_details": errors}


def get_sales_history(
    db: Session,
    product_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category: Optional[str] = None
) -> List[Sale]:
    query = db.query(Sale)
    if product_id:
        query = query.filter(Sale.product_id == product_id)
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    if category:
        query = query.join(Product).join(Product.category).filter(Product.category.has(name=category))
    return query.order_by(Sale.sale_date.desc()).all()


def get_sales_by_product(db: Session, product_id: int) -> dict:
    result = db.query(
        func.sum(Sale.total_amount).label("total_revenue"),
        func.sum(Sale.quantity).label("total_quantity"),
        func.count(Sale.id).label("total_transactions")
    ).filter(Sale.product_id == product_id).first()

    return {
        "product_id": product_id,
        "total_revenue": result.total_revenue or 0,
        "total_quantity": result.total_quantity or 0,
        "total_transactions": result.total_transactions or 0
    }


def get_sales_trends(db: Session, days: int = 90) -> List[dict]:
    start_date = datetime.utcnow() - timedelta(days=days)
    results = (
        db.query(
            func.date(Sale.sale_date).label("date"),
            func.sum(Sale.quantity).label("total_quantity"),
            func.sum(Sale.total_amount).label("total_revenue")
        )
        .filter(Sale.sale_date >= start_date)
        .group_by(func.date(Sale.sale_date))
        .order_by(func.date(Sale.sale_date))
        .all()
    )
    return [
        {
            "date": str(r.date),
            "total_quantity": r.total_quantity,
            "total_revenue": r.total_revenue
        }
        for r in results
    ]
