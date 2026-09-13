from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


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
