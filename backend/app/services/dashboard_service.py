from datetime import datetime, timedelta
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Product, Sale, Alert, Category, Transaction


def get_dashboard_stats(db: Session) -> dict:
    total_products = db.query(Product).count()
    inventory_value = db.query(
        func.sum(Product.current_stock * Product.unit_price)
    ).scalar() or 0
    unread_alerts = db.query(Alert).filter(Alert.is_read == False).count()
    low_stock_count = db.query(Product).filter(
        Product.current_stock <= Product.minimum_stock
    ).count()

    return {
        "total_products": total_products,
        "inventory_value": round(inventory_value, 2),
        "unread_alerts": unread_alerts,
        "low_stock_count": low_stock_count
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
            "total_quantity": r.total_quantity or 0,
            "total_revenue": round(r.total_revenue or 0, 2)
        }
        for r in results
    ]


def get_category_sales(db: Session) -> List[dict]:
    results = (
        db.query(
            Category.name.label("category_name"),
            func.sum(Sale.total_amount).label("total_revenue"),
            func.sum(Sale.quantity).label("total_quantity")
        )
        .join(Product, Category.id == Product.category_id)
        .join(Sale, Product.id == Sale.product_id)
        .group_by(Category.id)
        .all()
    )
    return [
        {
            "category_name": r.category_name,
            "total_revenue": round(r.total_revenue or 0, 2),
            "total_quantity": r.total_quantity or 0
        }
        for r in results
    ]


def get_top_products(db: Session, limit: int = 10) -> List[dict]:
    results = (
        db.query(
            Product.id,
            Product.name,
            func.sum(Sale.quantity).label("total_sold"),
            func.sum(Sale.total_amount).label("total_revenue")
        )
        .join(Sale, Product.id == Sale.product_id)
        .group_by(Product.id)
        .order_by(func.sum(Sale.quantity).desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "product_id": r.id,
            "product_name": r.name,
            "total_sold": r.total_sold or 0,
            "total_revenue": round(r.total_revenue or 0, 2)
        }
        for r in results
    ]


def get_lowest_products(db: Session, limit: int = 10) -> List[dict]:
    results = (
        db.query(
            Product.id,
            Product.name,
            func.sum(Sale.quantity).label("total_sold"),
            func.sum(Sale.total_amount).label("total_revenue")
        )
        .join(Sale, Product.id == Sale.product_id)
        .group_by(Product.id)
        .order_by(func.sum(Sale.quantity).asc())
        .limit(limit)
        .all()
    )
    return [
        {
            "product_id": r.id,
            "product_name": r.name,
            "total_sold": r.total_sold or 0,
            "total_revenue": round(r.total_revenue or 0, 2)
        }
        for r in results
    ]


def get_inventory_levels(db: Session) -> List[dict]:
    products = db.query(Product).all()
    return [
        {
            "product_id": p.id,
            "product_name": p.name,
            "current_stock": p.current_stock,
            "minimum_stock": p.minimum_stock,
            "maximum_stock": p.maximum_stock,
            "stock_status": (
                "out_of_stock" if p.current_stock == 0
                else "low" if p.current_stock <= p.minimum_stock
                else "overstock" if p.maximum_stock and p.current_stock > p.maximum_stock
                else "normal"
            )
        }
        for p in products
    ]


def get_demand_forecast_summary(db: Session) -> List[dict]:
    products = db.query(Product).limit(50).all()
    summary = []
    for product in products:
        recent_sales = (
            db.query(func.avg(Sale.quantity))
            .filter(Sale.product_id == product.id)
            .filter(Sale.sale_date >= datetime.utcnow() - timedelta(days=30))
            .scalar() or 0
        )
        summary.append({
            "product_id": product.id,
            "product_name": product.name,
            "current_stock": product.current_stock,
            "average_daily_demand": round(recent_sales, 2),
            "days_until_stockout": (
                int(product.current_stock / recent_sales)
                if recent_sales > 0 else None
            )
        })
    return summary
