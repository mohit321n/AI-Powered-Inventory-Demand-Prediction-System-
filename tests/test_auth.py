import pytest


class TestAuth:
    def test_register_user(self, client):
        response = client.post("/api/auth/register", json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "SecurePass123!",
            "full_name": "New User",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert data["full_name"] == "New User"
        assert "id" in data

    def test_login_user(self, client, test_user):
        response = client.post("/api/auth/login", data={
            "username": "testuser",
            "password": "TestPass123!",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_invalid_login(self, client, test_user):
        response = client.post("/api/auth/login", data={
            "username": "testuser",
            "password": "WrongPassword!",
        })
        assert response.status_code == 401

    def test_get_current_user(self, client, auth_headers):
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    def test_register_duplicate_username(self, client, test_user):
        response = client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "another@example.com",
            "password": "SecurePass123!",
            "full_name": "Another User",
        })
        assert response.status_code == 400

    def test_get_current_user_no_token(self, client):
        response = client.get("/api/auth/me")
        assert response.status_code == 401
