from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class SaleCreate(BaseModel):
    product_id: int
    units_sold: int
    selling_price: float
    promotion: bool = False
    discount: float = 0.0
    holiday: bool = False
    store_location: Optional[str] = None


class SaleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: datetime
    product_id: int
    product_name: Optional[str] = None
    category: Optional[str] = None
    units_sold: int
    selling_price: float
    promotion: bool
    discount: float
    holiday: bool
    store_location: Optional[str] = None
    stock_available: Optional[int] = None


class DatasetUploadResponse(BaseModel):
    message: str
    records_processed: int
    records_imported: int
    errors: List[str] = []
