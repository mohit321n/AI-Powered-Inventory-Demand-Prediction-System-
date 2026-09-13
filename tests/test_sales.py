import pytest
from datetime import datetime, timedelta


class TestSales:
    def test_add_sale(self, client, auth_headers, test_product):
        response = client.post("/api/sales/", json={
            "product_id": test_product.id,
            "quantity": 5,
            "unit_price": 29.99,
            "discount": 0.0,
            "notes": "Customer sale",
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["product_id"] == test_product.id
        assert data["quantity"] == 5
        assert data["total_price"] == 149.95

    def test_sales_history(self, client, auth_headers, test_product):
        client.post("/api/sales/", json={
            "product_id": test_product.id,
            "quantity": 3,
            "unit_price": 29.99,
        }, headers=auth_headers)
        client.post("/api/sales/", json={
            "product_id": test_product.id,
            "quantity": 2,
            "unit_price": 29.99,
        }, headers=auth_headers)

        response = client.get(
            f"/api/sales/?product_id={test_product.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_sales_trends(self, client, auth_headers, test_product):
        client.post("/api/sales/", json={
            "product_id": test_product.id,
            "quantity": 10,
            "unit_price": 29.99,
        }, headers=auth_headers)

        response = client.get("/api/sales/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    def test_sale_decrements_stock(self, client, auth_headers, test_product):
        initial_stock = test_product.current_stock
        client.post("/api/sales/", json={
            "product_id": test_product.id,
            "quantity": 15,
            "unit_price": 29.99,
        }, headers=auth_headers)

        response = client.get(f"/api/products/{test_product.id}", headers=auth_headers)
        assert response.json()["current_stock"] == initial_stock - 15

    def test_sale_insufficient_stock(self, client, auth_headers, test_product):
        response = client.post("/api/sales/", json={
            "product_id": test_product.id,
            "quantity": 9999,
            "unit_price": 29.99,
        }, headers=auth_headers)
        assert response.status_code == 400

    def test_sale_with_discount(self, client, auth_headers, test_product):
        response = client.post("/api/sales/", json={
            "product_id": test_product.id,
            "quantity": 10,
            "unit_price": 29.99,
            "discount": 50.0,
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["discount"] == 50.0
        assert data["total_price"] == 249.9

    def test_sale_product_not_found(self, client, auth_headers):
        response = client.post("/api/sales/", json={
            "product_id": 9999,
            "quantity": 1,
            "unit_price": 10.0,
        }, headers=auth_headers)
        assert response.status_code == 404

    def test_sales_unauthorized(self, client, test_product):
        response = client.post("/api/sales/", json={
            "product_id": test_product.id,
            "quantity": 1,
            "unit_price": 29.99,
        })
        assert response.status_code == 401
