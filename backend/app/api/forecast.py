from typing import Optional, List
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.auth import get_current_user
from app.models import Product, User, Sale, Forecast, ModelResult

router = APIRouter(prefix="/forecast", tags=["forecast"])


class TrainRequest(BaseModel):
    product_id: int
    models: List[str] = ["linear_regression", "random_forest", "xgboost"]


class TrainResponse(BaseModel):
    product_id: int
    status: str
    best_model: Optional[str] = None
    metrics: Optional[dict] = None


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


@router.post("/train", response_model=TrainResponse)
def train_model(
    request: TrainRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    sales = (
        db.query(Sale)
        .filter(Sale.product_id == request.product_id)
        .order_by(Sale.date)
        .all()
    )
    if len(sales) < 30:
        raise HTTPException(status_code=400, detail="Insufficient sales data (need at least 30 records)")

    try:
        import pandas as pd
        from ml.feature_engineering.feature_builder import FeatureBuilder
        from ml.training.model_trainer import ModelTrainer
        from ml.evaluation.metrics import ModelEvaluator

        df = pd.DataFrame([{
            "date": s.date,
            "units_sold": s.units_sold,
            "selling_price": s.selling_price,
            "promotion": s.promotion,
            "discount": s.discount,
            "holiday": s.holiday,
        } for s in sales])

        builder = FeatureBuilder()
        df_features = builder.build_features(df)
        df_features = df_features.dropna()

        feature_cols = [c for c in df_features.columns if c not in ["units_sold", "date"]]
        split_idx = int(len(df_features) * 0.8)
        train_df = df_features.iloc[:split_idx]
        test_df = df_features.iloc[split_idx:]

        X_train = train_df[feature_cols]
        y_train = train_df["units_sold"]
        X_test = test_df[feature_cols]
        y_test = test_df["units_sold"]

        trainer = ModelTrainer()
        evaluator = ModelEvaluator()
        comparison = trainer.compare_models(X_train, y_train, X_test, y_test)

        best_model_name = min(comparison.keys(), key=lambda k: comparison[k].get("mae", float("inf")))

        for model_name, metrics in comparison.items():
            result = ModelResult(
                model_name=model_name,
                product_id=request.product_id,
                mae=metrics.get("mae"),
                rmse=metrics.get("rmse"),
                mape=metrics.get("mape"),
                r2_score=metrics.get("r2"),
                is_best_model=(model_name == best_model_name),
            )
            db.add(result)
        db.commit()

        return TrainResponse(
            product_id=request.product_id,
            status="trained",
            best_model=best_model_name,
            metrics=comparison.get(best_model_name, {}),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@router.post("/predict", response_model=ForecastResponse)
def get_forecast(
    request: ForecastRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    sales = (
        db.query(Sale)
        .filter(Sale.product_id == request.product_id)
        .order_by(Sale.date)
        .all()
    )
    if len(sales) < 30:
        raise HTTPException(status_code=400, detail="Insufficient sales data")

    try:
        import pandas as pd
        import numpy as np
        from ml.feature_engineering.feature_builder import FeatureBuilder

        df = pd.DataFrame([{
            "date": s.date,
            "units_sold": s.units_sold,
            "selling_price": s.selling_price,
            "promotion": s.promotion,
            "discount": s.discount,
            "holiday": s.holiday,
        } for s in sales])

        builder = FeatureBuilder()
        df_features = builder.build_features(df)
        df_features = df_features.dropna()

        feature_cols = [c for c in df_features.columns if c not in ["units_sold", "date"]]
        X = df_features[feature_cols]
        y = df_features["units_sold"]

        model_name = request.model_name or "random_forest"
        trainer = ModelTrainer()

        if model_name == "linear_regression":
            model = trainer.train_linear_regression(X, y)
        elif model_name == "random_forest":
            model = trainer.train_random_forest(X, y)
        elif model_name == "xgboost":
            model = trainer.train_xgboost(X, y)
        else:
            model = trainer.train_random_forest(X, y)

        last_row = X.iloc[[-1]].copy()
        forecasts = []
        current_date = datetime.now()

        for i in range(request.periods):
            pred = model.predict(last_row)[0]
            pred = max(0, pred)
            forecast_date = current_date + pd.Timedelta(days=i + 1)
            forecasts.append(ForecastPoint(
                date=forecast_date.strftime("%Y-%m-%d"),
                predicted_demand=round(float(pred), 2),
                lower_bound=round(float(pred * 0.8), 2),
                upper_bound=round(float(pred * 1.2), 2),
            ))

        total_demand = sum(f.predicted_demand for f in forecasts)

        return ForecastResponse(
            product_id=request.product_id,
            model_used=model_name,
            forecasts=forecasts,
            total_predicted_demand=round(total_demand, 2),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecasting failed: {str(e)}")


@router.get("/compare/{product_id}", response_model=ModelComparisonResponse)
def compare_models(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    results = (
        db.query(ModelResult)
        .filter(ModelResult.product_id == product_id)
        .order_by(ModelResult.trained_at.desc())
        .all()
    )

    if not results:
        raise HTTPException(status_code=404, detail="No model results found. Train models first.")

    models = []
    best_model = None
    for r in results:
        models.append(ModelComparisonItem(
            model_name=r.model_name,
            mae=r.mae,
            rmse=r.rmse,
            mape=r.mape,
            r2_score=r.r2_score,
        ))
        if r.is_best_model:
            best_model = r.model_name

    return ModelComparisonResponse(
        product_id=product_id,
        models=models,
        best_model=best_model or models[0].model_name if models else "unknown",
    )


@router.post("/what-if", response_model=WhatIfResponse)
def what_if_analysis(
    request: WhatIfRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = db.query(Product).filter(Product.id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        import pandas as pd

        sales = (
            db.query(Sale)
            .filter(Sale.product_id == request.product_id)
            .order_by(Sale.date)
            .all()
        )

        df = pd.DataFrame([{
            "date": s.date,
            "units_sold": s.units_sold,
            "selling_price": s.selling_price,
            "promotion": s.promotion,
            "discount": s.discount,
            "holiday": s.holiday,
        } for s in sales])

        avg_daily_demand = df["units_sold"].mean()
        adjusted_demand = avg_daily_demand * (1 + request.demand_change_pct / 100)

        lead_time = product.lead_time_days + request.lead_time_change
        safety_stock = product.safety_stock + request.safety_stock_change
        reorder_point = adjusted_demand * lead_time + safety_stock

        current_date = datetime.now()
        baseline_forecast = []
        adjusted_forecast = []

        for i in range(30):
            fc_date = current_date + pd.Timedelta(days=i + 1)
            date_str = fc_date.strftime("%Y-%m-%d")
            baseline_forecast.append(ForecastPoint(
                date=date_str,
                predicted_demand=round(float(avg_daily_demand), 2),
            ))
            adjusted_forecast.append(ForecastPoint(
                date=date_str,
                predicted_demand=round(float(adjusted_demand), 2),
            ))

        stockout_days = product.current_stock / adjusted_demand if adjusted_demand > 0 else float("inf")
        recommendations = {
            "reorder_point": round(reorder_point, 0),
            "safety_stock": safety_stock,
            "lead_time_days": lead_time,
            "avg_daily_demand": round(adjusted_demand, 2),
            "estimated_stockout_days": round(stockout_days, 1),
            "needs_reorder": product.current_stock <= reorder_point,
        }

        return WhatIfResponse(
            product_id=request.product_id,
            baseline_forecast=baseline_forecast,
            adjusted_forecast=adjusted_forecast,
            parameters={
                "demand_change_pct": request.demand_change_pct,
                "lead_time_change": request.lead_time_change,
                "promotion_active": request.promotion_active,
                "safety_stock_change": request.safety_stock_change,
            },
            recommendations=recommendations,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"What-if analysis failed: {str(e)}")


@router.get("/reorder-recommendations", response_model=List[ReorderRecommendation])
def get_reorder_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    products = db.query(Product).all()
    recommendations = []

    for product in products:
        sales = (
            db.query(Sale)
            .filter(Sale.product_id == product.id)
            .order_by(Sale.date.desc())
            .limit(90)
            .all()
        )

        if not sales:
            continue

        avg_daily_demand = sum(s.units_sold for s in sales) / max(len(sales), 1)
        lead_time = product.lead_time_days
        safety_stock = product.safety_stock
        reorder_point = avg_daily_demand * lead_time + safety_stock

        if product.current_stock <= 0:
            priority = "critical"
            recommendation = "REORDER NOW"
            reason = f"Product is out of stock. Average daily demand is {avg_daily_demand:.1f} units."
        elif product.current_stock <= safety_stock:
            priority = "high"
            recommendation = "REORDER"
            reason = f"Stock ({product.current_stock}) is below safety stock ({safety_stock}). Predicted demand during lead time: {avg_daily_demand * lead_time:.0f} units."
        elif product.current_stock <= reorder_point:
            priority = "medium"
            recommendation = "REORDER SOON"
            reason = f"Stock ({product.current_stock}) is approaching reorder point ({reorder_point:.0f})."
        elif product.current_stock > reorder_point * 3:
            priority = "low"
            recommendation = "OVERSTOCK"
            reason = f"Stock ({product.current_stock}) significantly exceeds reorder point ({reorder_point:.0f}). Consider reducing orders."
        else:
            continue

        reorder_qty = max(int(avg_daily_demand * 30), product.minimum_stock)

        recommendations.append(ReorderRecommendation(
            product_id=product.id,
            product_name=product.name,
            current_stock=product.current_stock,
            reorder_point=int(reorder_point),
            reorder_quantity=reorder_qty,
            safety_stock=safety_stock,
            lead_time_days=lead_time,
            avg_daily_demand=round(avg_daily_demand, 2),
            priority=priority,
            recommendation=recommendation,
            reason=reason,
        ))

    return sorted(recommendations, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x.priority, 4))
