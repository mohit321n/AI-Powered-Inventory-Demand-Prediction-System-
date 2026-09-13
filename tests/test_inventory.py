import pytest
from datetime import datetime


class TestInventory:
    def test_add_transaction(self, client, auth_headers, test_product):
        response = client.post("/api/inventory/transactions", json={
            "product_id": test_product.id,
            "transaction_type": "inbound",
            "quantity": 50,
            "notes": "Restock delivery",
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["product_id"] == test_product.id
        assert data["transaction_type"] == "inbound"
        assert data["quantity"] == 50

    def test_get_inventory_history(self, client, auth_headers, test_product):
        client.post("/api/inventory/transactions", json={
            "product_id": test_product.id,
            "transaction_type": "inbound",
            "quantity": 25,
            "notes": "First restock",
        }, headers=auth_headers)
        client.post("/api/inventory/transactions", json={
            "product_id": test_product.id,
            "transaction_type": "outbound",
            "quantity": 10,
            "notes": "Sold",
        }, headers=auth_headers)

        response = client.get(
            f"/api/inventory/transactions?product_id={test_product.id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["transaction_type"] == "outbound"

    def test_stock_adjustment(self, client, auth_headers, test_product):
        response = client.put(
            f"/api/inventory/adjust/{test_product.id}",
            json={"new_stock": 200, "notes": "Annual count correction"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["transaction_type"] == "adjustment"
        assert data["quantity"] == 100

    def test_low_stock_detection(self, client, auth_headers, test_product_low_stock):
        response = client.get("/api/inventory/summary", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        low_stock_items = [s for s in data if s["current_stock"] <= s["minimum_stock"]]
        assert len(low_stock_items) >= 1
        assert low_stock_items[0]["product_name"] == "Low Stock Widget"

    def test_outbound_insufficient_stock(self, client, auth_headers, test_product):
        response = client.post("/api/inventory/transactions", json={
            "product_id": test_product.id,
            "transaction_type": "outbound",
            "quantity": 9999,
            "notes": "Too many",
        }, headers=auth_headers)
        assert response.status_code == 400

    def test_add_transaction_product_not_found(self, client, auth_headers):
        response = client.post("/api/inventory/transactions", json={
            "product_id": 9999,
            "transaction_type": "inbound",
            "quantity": 10,
        }, headers=auth_headers)
        assert response.status_code == 404

    def test_inbound_updates_stock(self, client, auth_headers, test_product):
        client.post("/api/inventory/transactions", json={
            "product_id": test_product.id,
            "transaction_type": "inbound",
            "quantity": 30,
            "notes": "Restock",
        }, headers=auth_headers)

        response = client.get(f"/api/products/{test_product.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["current_stock"] == 130

    def test_transaction_unauthorized(self, client, test_product):
        response = client.post("/api/inventory/transactions", json={
            "product_id": test_product.id,
            "transaction_type": "inbound",
            "quantity": 10,
        })
        assert response.status_code == 401
