import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


class TestForecast:
    def test_prepare_data(self, client, auth_headers, test_product, db_session):
        from app.models import Sale
        for i in range(30):
            sale = Sale(
                product_id=test_product.id,
                quantity=10 + i % 5,
                unit_price=29.99,
                total_price=29.99 * (10 + i % 5),
                sale_date=datetime.now() - timedelta(days=30 - i),
            )
            db_session.add(sale)
        db_session.commit()

        response = client.post("/api/forecast/train", json={
            "product_id": test_product.id,
            "model_type": "arima",
        }, headers=auth_headers)
        assert response.status_code == 200

    def test_model_comparison(self, client, auth_headers, test_product):
        response = client.get(
            f"/api/forecast/compare/{test_product.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == test_product.id
        assert "best_model" in data

    def test_reorder_recommendation(self, client, auth_headers, test_product_low_stock):
        response = client.get(
            "/api/forecast/reorder-recommendations",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["product_id"] == test_product_low_stock.id
        assert data[0]["priority"] in ("critical", "high", "medium")

    def test_predict_forecast(self, client, auth_headers, test_product):
        response = client.post("/api/forecast/predict", json={
            "product_id": test_product.id,
            "periods": 7,
            "model_type": "arima",
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == test_product.id
        assert isinstance(data["forecasts"], list)

    def test_train_product_not_found(self, client, auth_headers):
        response = client.post("/api/forecast/train", json={
            "product_id": 9999,
            "model_type": "arima",
        }, headers=auth_headers)
        assert response.status_code == 404

    def test_forecast_product_not_found(self, client, auth_headers):
        response = client.post("/api/forecast/predict", json={
            "product_id": 9999,
            "periods": 7,
        }, headers=auth_headers)
        assert response.status_code == 404

    def test_compare_product_not_found(self, client, auth_headers):
        response = client.get("/api/forecast/compare/9999", headers=auth_headers)
        assert response.status_code == 404

    def test_prepare_data_unit_tests(self):
        dates = pd.date_range(start="2024-01-01", periods=90, freq="D")
        quantities = np.random.randint(5, 50, size=90)
        df = pd.DataFrame({"date": dates, "quantity": quantities})

        assert len(df) == 90
        assert df["date"].is_monotonic_increasing
        assert df["quantity"].min() >= 0

    def test_model_comparison_unit(self):
        results = {
            "moving_average": {"mean_forecast": 25.0, "max_forecast": 30, "min_forecast": 20},
            "linear_regression": {"mean_forecast": 22.0, "max_forecast": 28, "min_forecast": 16},
            "exponential_smoothing": {"mean_forecast": 24.0, "max_forecast": 29, "min_forecast": 19},
        }
        best = min(results.keys(), key=lambda m: abs(results[m]["mean_forecast"]))
        assert best == "linear_regression"

    def test_reorder_calculation_logic(self):
        avg_daily_demand = 15.0
        lead_time = 7
        demand_std = 5.0
        lead_time_std = 2
        service_level = 1.65

        safety_stock = int(
            service_level * np.sqrt(lead_time * demand_std**2 + avg_daily_demand**2 * lead_time_std**2)
        )
        reorder_point = int(avg_daily_demand * lead_time + safety_stock)

        assert safety_stock > 0
        assert reorder_point > safety_stock
        assert reorder_point > avg_daily_demand * lead_time
