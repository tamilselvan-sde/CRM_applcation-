import os
import pytest
from typing import Generator

import httpx

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")


@pytest.fixture(scope="session")
def api_client() -> Generator[httpx.Client, None, None]:
    """Create a shared HTTP client for all tests."""
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        yield client


@pytest.fixture(scope="session")
def admin_token(api_client: httpx.Client) -> str:
    """Get admin authentication token."""
    response = api_client.post(
        "/auth/login",
        json={"email": "admin@crm.local", "password": "admin123"},
    )
    if response.status_code != 200:
        pytest.skip("Admin user not available - run database initialization first")
    return response.json()["access_token"]


@pytest.fixture(scope="session")
def admin_headers(admin_token: str) -> dict:
    """Get headers with admin authentication."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def test_user_data() -> dict:
    """Generate test user data."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return {
        "username": f"testuser_{unique_id}",
        "email": f"testuser_{unique_id}@test.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "role": "viewer",
    }


@pytest.fixture
def test_customer_data() -> dict:
    """Generate test customer data."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return {
        "name": f"Test Customer {unique_id}",
        "email": f"customer_{unique_id}@test.com",
        "phone": "+1-555-0100",
        "company": "Test Company",
        "address": "123 Test Street",
        "city": "Test City",
        "state": "TS",
        "postal_code": "12345",
        "country": "USA",
    }


@pytest.fixture
def test_product_data() -> dict:
    """Generate test product data."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return {
        "name": f"Test Product {unique_id}",
        "description": "A test product for E2E testing",
        "sku": f"TST-{unique_id}",
        "price": 99.99,
        "unit": "unit",
        "is_service": False,
        "is_active": True,
    }
