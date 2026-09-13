from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None


class SupplierCreate(BaseModel):
    name: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    lead_time_days: int = 7


class SupplierResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    lead_time_days: int


class ProductCreate(BaseModel):
    name: str
    sku: str
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    price: float
    cost_price: Optional[float] = None
    current_stock: int = 0
    minimum_stock: int = 10
    safety_stock: int = 5
    lead_time_days: int = 7


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    price: Optional[float] = None
    cost_price: Optional[float] = None
    current_stock: Optional[int] = None
    minimum_stock: Optional[int] = None
    safety_stock: Optional[int] = None
    lead_time_days: Optional[int] = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sku: str
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    price: float
    cost_price: Optional[float] = None
    current_stock: int
    minimum_stock: int
    safety_stock: int
    lead_time_days: int
