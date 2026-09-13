import pytest


class TestProducts:
    def test_create_product(self, client, auth_headers, test_category):
        response = client.post("/api/products/", json={
            "name": "New Widget",
            "sku": "PRD-001",
            "description": "A new widget",
            "category_id": test_category.id,
            "cost_price": 10.0,
            "selling_price": 25.0,
            "current_stock": 50,
            "minimum_stock": 10,
            "unit": "pcs",
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Widget"
        assert data["sku"] == "PRD-001"
        assert data["selling_price"] == 25.0
        assert data["current_stock"] == 50

    def test_get_product(self, client, auth_headers, test_product):
        response = client.get(f"/api/products/{test_product.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Widget"
        assert data["sku"] == "TST-001"
        assert data["price"] == 29.99

    def test_list_products(self, client, auth_headers, test_product):
        response = client.get("/api/products/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1
        assert data["items"][0]["sku"] == "TST-001"

    def test_update_product(self, client, auth_headers, test_product):
        response = client.put(f"/api/products/{test_product.id}", json={
            "name": "Updated Widget",
            "selling_price": 35.0,
        }, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Widget"
        assert data["selling_price"] == 35.0

    def test_delete_product(self, client, auth_headers, test_product):
        response = client.delete(f"/api/products/{test_product.id}", headers=auth_headers)
        assert response.status_code == 204

        get_response = client.get(f"/api/products/{test_product.id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_create_category(self, client, auth_headers):
        response = client.post("/api/products/categories/", json={
            "name": "Furniture",
            "description": "Office furniture",
        }, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Furniture"
        assert data["description"] == "Office furniture"

    def test_create_product_duplicate_sku(self, client, auth_headers, test_product):
        response = client.post("/api/products/", json={
            "name": "Another Widget",
            "sku": "TST-001",
            "cost_price": 10.0,
            "selling_price": 25.0,
        }, headers=auth_headers)
        assert response.status_code == 400

    def test_get_product_not_found(self, client, auth_headers):
        response = client.get("/api/products/9999", headers=auth_headers)
        assert response.status_code == 404

    def test_list_products_search(self, client, auth_headers, test_product):
        response = client.get("/api/products/?search=Widget", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    def test_create_product_unauthorized(self, client):
        response = client.post("/api/products/", json={
            "name": "Unauthorized Widget",
            "sku": "UNA-001",
            "cost_price": 10.0,
            "selling_price": 25.0,
        })
        assert response.status_code == 401
