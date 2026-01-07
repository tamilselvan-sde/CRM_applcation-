"""
E2E Tests for User Login
Tests the complete user login and authentication flow.
"""
import pytest
import httpx


class TestUserLogin:
    """Test suite for user login functionality."""

    def test_login_success(self, api_client: httpx.Client, test_user_data: dict):
        """Test successful user login."""
        api_client.post("/auth/register", json=test_user_data)
        
        response = api_client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_email_fails(self, api_client: httpx.Client):
        """Test that login with non-existent email fails."""
        response = api_client.post(
            "/auth/login",
            json={
                "email": "nonexistent@test.com",
                "password": "SomePassword123!",
            },
        )
        
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_login_invalid_password_fails(
        self, api_client: httpx.Client, test_user_data: dict
    ):
        """Test that login with wrong password fails."""
        api_client.post("/auth/register", json=test_user_data)
        
        response = api_client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": "WrongPassword123!",
            },
        )
        
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    def test_get_current_user(self, api_client: httpx.Client, test_user_data: dict):
        """Test getting current user information with valid token."""
        api_client.post("/auth/register", json=test_user_data)
        
        login_response = api_client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        token = login_response.json()["access_token"]
        
        response = api_client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]

    def test_access_protected_route_without_token_fails(
        self, api_client: httpx.Client
    ):
        """Test that accessing protected routes without token fails."""
        response = api_client.get("/auth/me")
        
        assert response.status_code in [401, 403]

    def test_access_protected_route_with_invalid_token_fails(
        self, api_client: httpx.Client
    ):
        """Test that accessing protected routes with invalid token fails."""
        response = api_client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )
        
        assert response.status_code == 401

    def test_token_contains_user_info(
        self, api_client: httpx.Client, test_user_data: dict
    ):
        """Test that JWT token can be used to access user info."""
        api_client.post("/auth/register", json=test_user_data)
        
        login_response = api_client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        me_response = api_client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert me_response.status_code == 200
        user_data = me_response.json()
        assert user_data["role"] == test_user_data["role"]
