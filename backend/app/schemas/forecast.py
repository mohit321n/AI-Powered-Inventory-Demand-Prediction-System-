from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class ForecastRequest(BaseModel):
    product_id: int
    periods: int = 30
    model_name: Optional[str] = None


class ForecastPoint(BaseModel):
    date: str
    predicted_demand: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None


class ForecastResponse(BaseModel):
    product_id: int
    model_used: str
    forecasts: List[ForecastPoint]
    total_predicted_demand: float


class ModelComparisonItem(BaseModel):
    model_name: str
    mae: Optional[float] = None
    rmse: Optional[float] = None
    mape: Optional[float] = None
    r2_score: Optional[float] = None


class ModelComparisonResponse(BaseModel):
    product_id: int
    models: List[ModelComparisonItem]
    best_model: str


class ReorderRecommendation(BaseModel):
    product_id: int
    product_name: str
    current_stock: int
    reorder_point: int
    reorder_quantity: int
    safety_stock: int
    lead_time_days: int
    avg_daily_demand: float
    priority: str
    recommendation: str
    reason: str


class WhatIfRequest(BaseModel):
    product_id: int
    demand_change_pct: Optional[float] = 0.0
    lead_time_change: Optional[int] = 0
    promotion_active: Optional[bool] = False
    safety_stock_change: Optional[int] = 0


class WhatIfResponse(BaseModel):
    product_id: int
    baseline_forecast: List[ForecastPoint]
    adjusted_forecast: List[ForecastPoint]
    parameters: dict
    recommendations: dict
