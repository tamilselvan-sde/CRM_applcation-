"""
E2E Tests for User Registration
Tests the complete user registration flow.
"""
import pytest
import httpx


class TestUserRegistration:
    """Test suite for user registration functionality."""

    def test_register_new_user_success(
        self, api_client: httpx.Client, test_user_data: dict
    ):
        """Test successful user registration."""
        response = api_client.post("/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert data["role"] == test_user_data["role"]
        assert data["is_active"] is True
        assert "_id" in data
        assert "password" not in data

    def test_register_duplicate_email_fails(
        self, api_client: httpx.Client, test_user_data: dict
    ):
        """Test that registering with duplicate email fails."""
        api_client.post("/auth/register", json=test_user_data)
        
        response = api_client.post("/auth/register", json=test_user_data)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_register_duplicate_username_fails(
        self, api_client: httpx.Client, test_user_data: dict
    ):
        """Test that registering with duplicate username fails."""
        api_client.post("/auth/register", json=test_user_data)
        
        test_user_data["email"] = "different@test.com"
        response = api_client.post("/auth/register", json=test_user_data)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_register_invalid_email_fails(self, api_client: httpx.Client):
        """Test that registration with invalid email fails."""
        response = api_client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "invalid-email",
                "password": "TestPassword123!",
            },
        )
        
        assert response.status_code == 422

    def test_register_short_password_fails(self, api_client: httpx.Client):
        """Test that registration with short password fails."""
        response = api_client.post(
            "/auth/register",
            json={
                "username": "testuser",
                "email": "test@test.com",
                "password": "short",
            },
        )
        
        assert response.status_code == 422

    def test_register_invalid_role_fails(
        self, api_client: httpx.Client, test_user_data: dict
    ):
        """Test that registration with invalid role fails."""
        test_user_data["role"] = "superadmin"
        
        response = api_client.post("/auth/register", json=test_user_data)
        
        assert response.status_code == 400
        assert "role" in response.json()["detail"].lower()

    def test_register_with_all_roles(self, api_client: httpx.Client):
        """Test registration with all valid roles."""
        import uuid
        
        roles = ["admin", "manager", "staff", "viewer"]
        
        for role in roles:
            unique_id = str(uuid.uuid4())[:8]
            user_data = {
                "username": f"user_{role}_{unique_id}",
                "email": f"user_{role}_{unique_id}@test.com",
                "password": "TestPassword123!",
                "role": role,
            }
            
            response = api_client.post("/auth/register", json=user_data)
            
            assert response.status_code == 201, f"Failed to register user with role {role}"
            assert response.json()["role"] == role
