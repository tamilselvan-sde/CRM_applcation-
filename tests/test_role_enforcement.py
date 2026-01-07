"""
E2E Tests for Role Enforcement
Tests that permissions are properly enforced at API level.
"""
import pytest
import httpx


class TestRoleEnforcement:
    """Test suite for role-based access control."""

    @pytest.fixture
    def viewer_token(self, api_client: httpx.Client) -> str:
        """Create a viewer user and get token."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "username": f"viewer_{unique_id}",
            "email": f"viewer_{unique_id}@test.com",
            "password": "TestPassword123!",
            "role": "viewer",
        }
        api_client.post("/auth/register", json=user_data)
        response = api_client.post(
            "/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]},
        )
        return response.json()["access_token"]

    @pytest.fixture
    def staff_token(self, api_client: httpx.Client) -> str:
        """Create a staff user and get token."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "username": f"staff_{unique_id}",
            "email": f"staff_{unique_id}@test.com",
            "password": "TestPassword123!",
            "role": "staff",
        }
        api_client.post("/auth/register", json=user_data)
        response = api_client.post(
            "/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]},
        )
        return response.json()["access_token"]

    @pytest.fixture
    def manager_token(self, api_client: httpx.Client) -> str:
        """Create a manager user and get token."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "username": f"manager_{unique_id}",
            "email": f"manager_{unique_id}@test.com",
            "password": "TestPassword123!",
            "role": "manager",
        }
        api_client.post("/auth/register", json=user_data)
        response = api_client.post(
            "/auth/login",
            json={"email": user_data["email"], "password": user_data["password"]},
        )
        return response.json()["access_token"]

    def test_viewer_can_read_customers(
        self, api_client: httpx.Client, viewer_token: str
    ):
        """Test that viewer can read customers."""
        response = api_client.get(
            "/customers",
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
        assert response.status_code == 200

    def test_viewer_cannot_create_customer(
        self, api_client: httpx.Client, viewer_token: str, test_customer_data: dict
    ):
        """Test that viewer cannot create customers."""
        response = api_client.post(
            "/customers",
            json=test_customer_data,
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
        assert response.status_code == 403

    def test_viewer_cannot_delete_customer(
        self, api_client: httpx.Client, viewer_token: str, admin_headers: dict,
        test_customer_data: dict
    ):
        """Test that viewer cannot delete customers."""
        create_response = api_client.post(
            "/customers",
            json=test_customer_data,
            headers=admin_headers,
        )
        customer_id = create_response.json()["id"]
        
        response = api_client.delete(
            f"/customers/{customer_id}",
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
        assert response.status_code == 403

    def test_staff_can_read_products(
        self, api_client: httpx.Client, staff_token: str
    ):
        """Test that staff can read products."""
        response = api_client.get(
            "/products",
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 200

    def test_staff_cannot_create_product(
        self, api_client: httpx.Client, staff_token: str, test_product_data: dict
    ):
        """Test that staff cannot create products."""
        response = api_client.post(
            "/products",
            json=test_product_data,
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 403

    def test_staff_can_create_invoice(
        self, api_client: httpx.Client, staff_token: str, admin_headers: dict,
        test_customer_data: dict, test_product_data: dict
    ):
        """Test that staff can create invoices."""
        customer_response = api_client.post(
            "/customers",
            json=test_customer_data,
            headers=admin_headers,
        )
        customer_id = customer_response.json()["id"]
        
        product_response = api_client.post(
            "/products",
            json=test_product_data,
            headers=admin_headers,
        )
        product_id = product_response.json()["id"]
        
        invoice_data = {
            "customer_id": customer_id,
            "status": "draft",
            "tax_rate": 10,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 2,
                    "unit_price": test_product_data["price"],
                }
            ],
        }
        
        response = api_client.post(
            "/invoices",
            json=invoice_data,
            headers={"Authorization": f"Bearer {staff_token}"},
        )
        assert response.status_code == 201

    def test_manager_can_create_customer(
        self, api_client: httpx.Client, manager_token: str, test_customer_data: dict
    ):
        """Test that manager can create customers."""
        response = api_client.post(
            "/customers",
            json=test_customer_data,
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        assert response.status_code == 201

    def test_manager_can_create_product(
        self, api_client: httpx.Client, manager_token: str, test_product_data: dict
    ):
        """Test that manager can create products."""
        response = api_client.post(
            "/products",
            json=test_product_data,
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        assert response.status_code == 201

    def test_manager_can_delete_customer(
        self, api_client: httpx.Client, manager_token: str, test_customer_data: dict
    ):
        """Test that manager can delete customers."""
        create_response = api_client.post(
            "/customers",
            json=test_customer_data,
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        customer_id = create_response.json()["id"]
        
        response = api_client.delete(
            f"/customers/{customer_id}",
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        assert response.status_code == 204

    def test_admin_can_access_users_endpoint(
        self, api_client: httpx.Client, admin_headers: dict
    ):
        """Test that admin can access users management."""
        response = api_client.get("/auth/users", headers=admin_headers)
        assert response.status_code == 200

    def test_non_admin_cannot_access_users_endpoint(
        self, api_client: httpx.Client, manager_token: str
    ):
        """Test that non-admin cannot access users management."""
        response = api_client.get(
            "/auth/users",
            headers={"Authorization": f"Bearer {manager_token}"},
        )
        assert response.status_code == 403

    def test_admin_can_update_user_role(
        self, api_client: httpx.Client, admin_headers: dict, test_user_data: dict
    ):
        """Test that admin can update user roles."""
        register_response = api_client.post("/auth/register", json=test_user_data)
        user_id = register_response.json()["_id"]
        
        response = api_client.put(
            f"/auth/users/{user_id}",
            json={"role": "manager"},
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        assert response.json()["role"] == "manager"
