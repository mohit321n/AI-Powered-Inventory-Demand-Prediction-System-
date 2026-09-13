import pytest
import numpy as np


class TestReorderCalculations:
    def test_reorder_point_calculation(self):
        avg_daily_demand = 20.0
        lead_time_days = 10
        safety_stock = 50

        reorder_point = (avg_daily_demand * lead_time_days) + safety_stock

        assert reorder_point == 250
        assert reorder_point > avg_daily_demand * lead_time_days
        assert reorder_point > safety_stock

    def test_reorder_point_with_varying_lead_time(self):
        avg_daily_demand = 15.0
        lead_times = [5, 7, 14, 30]
        safety_stock = 30

        reorder_points = []
        for lt in lead_times:
            rp = (avg_daily_demand * lt) + safety_stock
            reorder_points.append(rp)

        assert reorder_points == sorted(reorder_points)
        assert reorder_points[-1] > reorder_points[0]

    def test_safety_stock_calculation(self):
        z_score = 1.65
        lead_time_days = 7
        demand_std = 10.0
        avg_demand = 20.0
        lead_time_std = 2

        safety_stock = int(
            z_score * np.sqrt(
                lead_time_days * demand_std**2 + avg_demand**2 * lead_time_std**2
            )
        )

        assert safety_stock > 0
        assert safety_stock > z_score * demand_std * np.sqrt(lead_time_days)

    def test_safety_stock_service_levels(self):
        service_levels = {
            "90%": 1.28,
            "95%": 1.65,
            "99%": 2.33,
        }
        lead_time_days = 7
        demand_std = 10.0
        avg_demand = 20.0
        lead_time_std = 2

        safety_stocks = {}
        for level, z in service_levels.items():
            ss = int(
                z * np.sqrt(
                    lead_time_days * demand_std**2 + avg_demand**2 * lead_time_std**2
                )
            )
            safety_stocks[level] = ss

        assert safety_stocks["90%"] < safety_stocks["95%"] < safety_stocks["99%"]

    def test_eoq_calculation(self):
        annual_demand = 1000
        ordering_cost = 50
        holding_cost = 2

        eoq = np.sqrt((2 * annual_demand * ordering_cost) / holding_cost)

        assert eoq > 0
        assert eoq == pytest.approx(223.6, rel=0.1)

    def test_eoq_sensitivity_to_ordering_cost(self):
        annual_demand = 1000
        ordering_costs = [10, 50, 100]
        holding_cost = 2

        eoqs = [np.sqrt((2 * annual_demand * oc) / holding_cost) for oc in ordering_costs]

        assert eoqs == sorted(eoqs)
        assert eoqs[0] < eoqs[-1]

    def test_eoq_sensitivity_to_holding_cost(self):
        annual_demand = 1000
        ordering_cost = 50
        holding_costs = [1, 2, 5]

        eoqs = [np.sqrt((2 * annual_demand * ordering_cost) / hc) for hc in holding_costs]

        assert eoqs[0] > eoqs[-1]

    def test_reorder_priority_logic(self):
        products = [
            {"name": "Critical Item", "current_stock": 0, "minimum_stock": 10},
            {"name": "High Item", "current_stock": 3, "minimum_stock": 10},
            {"name": "Medium Item", "current_stock": 8, "minimum_stock": 10},
            {"name": "OK Item", "current_stock": 15, "minimum_stock": 10},
        ]

        recommendations = []
        for p in products:
            if p["current_stock"] == 0:
                priority = "critical"
            elif p["current_stock"] <= p["minimum_stock"] * 0.5:
                priority = "high"
            elif p["current_stock"] <= p["minimum_stock"]:
                priority = "medium"
            else:
                priority = "low"

            reorder_qty = max(p["minimum_stock"] * 2 - p["current_stock"], p["minimum_stock"])
            recommendations.append({
                "product_name": p["name"],
                "priority": priority,
                "reorder_quantity": reorder_qty,
            })

        assert recommendations[0]["priority"] == "critical"
        assert recommendations[1]["priority"] == "high"
        assert recommendations[2]["priority"] == "medium"
        assert recommendations[3]["priority"] == "low"

    def test_reorder_quantity_calculation(self):
        minimum_stock = 10
        current_stock = 3

        reorder_quantity = max(minimum_stock * 2 - current_stock, minimum_stock)
        assert reorder_quantity == 17

        current_stock = 15
        reorder_quantity = max(minimum_stock * 2 - current_stock, minimum_stock)
        assert reorder_quantity == 10

    def test_economic_order_quantity_integer(self):
        annual_demand = 1200
        ordering_cost = 75
        holding_cost = 3

        eoq = int(np.sqrt((2 * annual_demand * ordering_cost) / holding_cost))
        assert isinstance(eoq, int)
        assert eoq > 0
