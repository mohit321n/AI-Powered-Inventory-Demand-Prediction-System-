from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    alert_type: str
    severity: str
    message: str
    is_read: bool = False
    created_at: datetime


class AlertSummary(BaseModel):
    total: int
    unread: int
    critical: int
    high: int
    medium: int
    low: int
