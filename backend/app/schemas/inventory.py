from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class InventoryTransactionCreate(BaseModel):
    product_id: int
    transaction_type: str  # "inbound", "outbound", "adjustment"
    quantity: int
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class InventoryTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    transaction_type: str
    quantity: int
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime


class InventorySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int
    product_name: str
    current_stock: int
    minimum_stock: int
    total_inbound: int
    total_outbound: int
    net_movement: int
