from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.auth import get_current_user
from app.models import Product, Sale, InventoryTransaction, Alert, User

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class DashboardStats(BaseModel):
    total_products: int
    low_stock_products: int
    overstock_products: int
    total_sales_today: int
    total_sales_month: int
    total_transactions: int
    active_alerts: int
    total_inventory_value: float


class SalesTrend(BaseModel):
    date: str
    total_sales: float
    total_quantity: int


class CategorySales(BaseModel):
    category_name: str
    total_sales: float
    total_quantity: int


class TopProduct(BaseModel):
    product_id: int
    product_name: str
    total_quantity_sold: int
    total_revenue: float


class InventoryTrend(BaseModel):
    date: str
    inbound: int
    outbound: int


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = datetime.utcnow().date()
    month_start = today.replace(day=1)

    total_products = db.query(Product).count()
    low_stock_products = db.query(Product).filter(Product.current_stock <= Product.minimum_stock).count()
    overstock_products = db.query(Product).filter(Product.current_stock > Product.minimum_stock * 5).count()

    total_sales_today = db.query(func.coalesce(func.sum(Sale.units_sold), 0)).filter(
        func.date(Sale.date) == today
    ).scalar()

    total_sales_month = db.query(func.coalesce(func.sum(Sale.units_sold), 0)).filter(
        Sale.date >= datetime.combine(month_start, datetime.min.time())
    ).scalar()

    total_transactions = db.query(InventoryTransaction).count()
    active_alerts = db.query(Alert).filter(Alert.is_read == False).count()

    inventory_value = db.query(
        func.coalesce(func.sum(Product.current_stock * Product.price), 0)
    ).scalar()

    return DashboardStats(
        total_products=total_products,
        low_stock_products=low_stock_products,
        overstock_products=overstock_products,
        total_sales_today=int(total_sales_today),
        total_sales_month=int(total_sales_month),
        total_transactions=total_transactions,
        active_alerts=active_alerts,
        total_inventory_value=float(inventory_value),
    )


@router.get("/sales-trends", response_model=list[SalesTrend])
def get_sales_trends(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start_date = datetime.utcnow() - timedelta(days=days)
    results = db.query(
        func.date(Sale.date).label("date"),
        func.sum(Sale.units_sold * Sale.selling_price).label("total_sales"),
        func.sum(Sale.units_sold).label("total_quantity"),
    ).filter(
        Sale.date >= start_date
    ).group_by(
        func.date(Sale.date)
    ).order_by(
        func.date(Sale.date)
    ).all()

    return [SalesTrend(
        date=str(r.date),
        total_sales=float(r.total_sales or 0),
        total_quantity=int(r.total_quantity or 0),
    ) for r in results]


@router.get("/category-sales", response_model=list[CategorySales])
def get_category_sales(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start_date = datetime.utcnow() - timedelta(days=days)
    results = db.query(
        Sale.category,
        func.sum(Sale.units_sold * Sale.selling_price).label("total_sales"),
        func.sum(Sale.units_sold).label("total_quantity"),
    ).filter(
        Sale.date >= start_date,
        Sale.category.isnot(None),
    ).group_by(Sale.category).all()

    return [CategorySales(
        category_name=r.category or "Uncategorized",
        total_sales=float(r.total_sales or 0),
        total_quantity=int(r.total_quantity or 0),
    ) for r in results]


@router.get("/top-products", response_model=list[TopProduct])
def get_top_products(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start_date = datetime.utcnow() - timedelta(days=days)
    results = db.query(
        Sale.product_id,
        Sale.product_name,
        func.sum(Sale.units_sold).label("total_quantity_sold"),
        func.sum(Sale.units_sold * Sale.selling_price).label("total_revenue"),
    ).filter(
        Sale.date >= start_date
    ).group_by(
        Sale.product_id, Sale.product_name
    ).order_by(
        func.sum(Sale.units_sold * Sale.selling_price).desc()
    ).limit(limit).all()

    return [TopProduct(
        product_id=r.product_id,
        product_name=r.product_name or "Unknown",
        total_quantity_sold=int(r.total_quantity_sold or 0),
        total_revenue=float(r.total_revenue or 0),
    ) for r in results]


@router.get("/inventory-trends", response_model=list[InventoryTrend])
def get_inventory_trends(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start_date = datetime.utcnow() - timedelta(days=days)
    inbound = db.query(
        func.date(InventoryTransaction.created_at).label("date"),
        func.sum(InventoryTransaction.quantity).label("total"),
    ).filter(
        InventoryTransaction.transaction_type == "inbound",
        InventoryTransaction.created_at >= start_date,
    ).group_by(func.date(InventoryTransaction.created_at)).all()

    outbound = db.query(
        func.date(InventoryTransaction.created_at).label("date"),
        func.sum(InventoryTransaction.quantity).label("total"),
    ).filter(
        InventoryTransaction.transaction_type == "outbound",
        InventoryTransaction.created_at >= start_date,
    ).group_by(func.date(InventoryTransaction.created_at)).all()

    dates = {}
    for r in inbound:
        d = str(r.date)
        dates[d] = {"date": d, "inbound": int(r.total or 0), "outbound": 0}
    for r in outbound:
        d = str(r.date)
        if d in dates:
            dates[d]["outbound"] = int(r.total or 0)
        else:
            dates[d] = {"date": d, "inbound": 0, "outbound": int(r.total or 0)}

    return [InventoryTrend(**v) for v in sorted(dates.values(), key=lambda x: x["date"])]
