from datetime import datetime, timedelta
from typing import List, Optional

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from app.models import Product, Sale, Transaction, Category
from app.schemas import WhatIfScenario


def prepare_forecast_data(
    db: Session,
    product_id: Optional[int] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> pd.DataFrame:
    query = db.query(Sale)
    if product_id:
        query = query.filter(Sale.product_id == product_id)
    if category:
        query = query.join(Product).join(Category).filter(Category.name == category)
    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)

    sales = query.all()
    data = [
        {
            "date": s.sale_date,
            "product_id": s.product_id,
            "quantity": s.quantity,
            "revenue": s.total_amount
        }
        for s in sales
    ]
    df = pd.DataFrame(data)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
    return df


def train_models(db: Session, product_id: int, model_names: List[str]) -> dict:
    df = prepare_forecast_data(db, product_id=product_id)
    if df.empty:
        return {"message": "No historical data available for training", "models_trained": []}

    df = df.set_index("date").resample("D")["quantity"].sum().fillna(0)
    results = {}

    for model_name in model_names:
        try:
            if model_name == "moving_average":
                df_smooth = df.rolling(window=7).mean()
                results[model_name] = {"status": "trained", "data_points": len(df)}
            elif model_name == "exponential_smoothing":
                df_smooth = df.ewm(span=7).mean()
                results[model_name] = {"status": "trained", "data_points": len(df)}
            elif model_name == "linear_regression":
                results[model_name] = {"status": "trained", "data_points": len(df)}
            else:
                results[model_name] = {"status": "unknown_model"}
        except Exception as e:
            results[model_name] = {"status": "error", "message": str(e)}

    return {"models_trained": results}


def generate_forecast(db: Session, product_id: int, model_name: str, periods: int) -> List[dict]:
    df = prepare_forecast_data(db, product_id=product_id)
    if df.empty:
        return []

    df = df.set_index("date").resample("D")["quantity"].sum().fillna(0)

    if model_name == "moving_average":
        forecast_values = [df.rolling(window=7).mean().iloc[-1]] * periods
    elif model_name == "exponential_smoothing":
        forecast_values = [df.ewm(span=7).mean().iloc[-1]] * periods
    elif model_name == "linear_regression":
        x = np.arange(len(df))
        y = df.values
        coeffs = np.polyfit(x, y, 1)
        future_x = np.arange(len(df), len(df) + periods)
        forecast_values = np.polyval(coeffs, future_x).tolist()
    else:
        forecast_values = [df.mean()] * periods

    last_date = df.index[-1]
    forecasts = []
    for i, value in enumerate(forecast_values):
        forecasts.append({
            "date": str(last_date + timedelta(days=i + 1)),
            "forecasted_quantity": max(0, int(value)),
            "model_used": model_name
        })
    return forecasts


def get_model_comparison(db: Session, product_id: int) -> dict:
    models = ["moving_average", "exponential_smoothing", "linear_regression"]
    comparison = {}
    for model in models:
        forecast = generate_forecast(db, product_id, model, 30)
        if forecast:
            values = [f["forecasted_quantity"] for f in forecast]
            comparison[model] = {
                "mean_forecast": sum(values) / len(values),
                "max_forecast": max(values),
                "min_forecast": min(values)
            }
    return comparison


def get_best_model(db: Session, product_id: int) -> str:
    comparison = get_model_comparison(db, product_id)
    if not comparison:
        return "moving_average"
    return min(comparison.keys(), key=lambda m: abs(comparison[m]["mean_forecast"]))


def what_if_analysis(db: Session, product_id: int, scenarios: List[WhatIfScenario]) -> List[dict]:
    results = []
    for scenario in scenarios:
        df = prepare_forecast_data(db, product_id=product_id)
        if not df.empty:
            df = df.set_index("date").resample("D")["quantity"].sum().fillna(0)

            if scenario.demand_change:
                df = df * (1 + scenario.demand_change / 100)

            if scenario.lead_time_change:
                df = df.rolling(window=7 + scenario.lead_time_change).mean().fillna(0)

            results.append({
                "scenario_name": scenario.name,
                "demand_change": scenario.demand_change,
                "lead_time_change": scenario.lead_time_change,
                "projected_average": df.mean(),
                "projected_max": df.max()
            })
    return results


def calculate_reorder_recommendation(db: Session, product_id: int) -> dict:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {}

    df = prepare_forecast_data(db, product_id=product_id)
    if df.empty:
        return {
            "product_id": product_id,
            "reorder_point": product.minimum_stock * 2,
            "economic_order_quantity": product.maximum_stock // 2,
            "safety_stock": product.minimum_stock
        }

    daily_demand = df.set_index("date").resample("D")["quantity"].sum().fillna(0)
    avg_demand = daily_demand.mean()
    demand_std = daily_demand.std()

    lead_time = 7
    lead_time_std = 2
    service_level = 1.65

    safety_stock = int(service_level * np.sqrt(lead_time * demand_std**2 + avg_demand**2 * lead_time_std**2))
    reorder_point = int(avg_demand * lead_time + safety_stock)

    ordering_cost = 50
    holding_cost = 2
    annual_demand = avg_demand * 365
    eoq = int(np.sqrt((2 * annual_demand * ordering_cost) / holding_cost))

    return {
        "product_id": product_id,
        "average_daily_demand": round(avg_demand, 2),
        "lead_time_days": lead_time,
        "safety_stock": safety_stock,
        "reorder_point": reorder_point,
        "economic_order_quantity": eoq,
        "current_stock": product.current_stock
    }
