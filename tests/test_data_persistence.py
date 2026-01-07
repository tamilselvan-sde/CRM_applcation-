"""
E2E Tests for Data Persistence
Tests that data is properly persisted in PostgreSQL and MongoDB.
"""
import pytest
import httpx


class TestDataPersistence:
    """Test suite for data persistence functionality."""

    def test_customer_data_persists(
        self, api_client: httpx.Client, admin_headers: dict,
        test_customer_data: dict
    ):
        """Test that customer data persists after creation."""
        create_response = api_client.post(
            "/customers",
            json=test_customer_data,
            headers=admin_headers,
        )
        
        assert create_response.status_code == 201
        customer_id = create_response.json()["id"]
        
        get_response = api_client.get(
            f"/customers/{customer_id}",
            headers=admin_headers,
        )
        
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["name"] == test_customer_data["name"]
        assert data["email"] == test_customer_data["email"]
        assert data["phone"] == test_customer_data["phone"]
        assert data["company"] == test_customer_data["company"]

    def test_customer_update_persists(
        self, api_client: httpx.Client, admin_headers: dict,
        test_customer_data: dict
    ):
        """Test that customer updates persist."""
        create_response = api_client.post(
            "/customers",
            json=test_customer_data,
            headers=admin_headers,
        )
        customer_id = create_response.json()["id"]
        
        updated_data = {
            "name": "Updated Customer Name",
            "company": "Updated Company",
        }
        
        update_response = api_client.put(
            f"/customers/{customer_id}",
            json=updated_data,
            headers=admin_headers,
        )
        
        assert update_response.status_code == 200
        
        get_response = api_client.get(
            f"/customers/{customer_id}",
            headers=admin_headers,
        )
        
        assert get_response.json()["name"] == updated_data["name"]
        assert get_response.json()["company"] == updated_data["company"]

    def test_product_data_persists(
        self, api_client: httpx.Client, admin_headers: dict,
        test_product_data: dict
    ):
        """Test that product data persists after creation."""
        create_response = api_client.post(
            "/products",
            json=test_product_data,
            headers=admin_headers,
        )
        
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        get_response = api_client.get(
            f"/products/{product_id}",
            headers=admin_headers,
        )
        
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["name"] == test_product_data["name"]
        assert data["sku"] == test_product_data["sku"]
        assert float(data["price"]) == test_product_data["price"]

    def test_product_update_persists(
        self, api_client: httpx.Client, admin_headers: dict,
        test_product_data: dict
    ):
        """Test that product updates persist."""
        create_response = api_client.post(
            "/products",
            json=test_product_data,
            headers=admin_headers,
        )
        product_id = create_response.json()["id"]
        
        updated_data = {
            "name": "Updated Product Name",
            "price": 199.99,
        }
        
        update_response = api_client.put(
            f"/products/{product_id}",
            json=updated_data,
            headers=admin_headers,
        )
        
        assert update_response.status_code == 200
        
        get_response = api_client.get(
            f"/products/{product_id}",
            headers=admin_headers,
        )
        
        assert get_response.json()["name"] == updated_data["name"]
        assert float(get_response.json()["price"]) == updated_data["price"]

    def test_invoice_data_persists(
        self, api_client: httpx.Client, admin_headers: dict,
        test_customer_data: dict, test_product_data: dict
    ):
        """Test that invoice data persists after creation."""
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
            "notes": "Persistence test invoice",
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 3,
                    "unit_price": test_product_data["price"],
                }
            ],
        }
        
        create_response = api_client.post(
            "/invoices",
            json=invoice_data,
            headers=admin_headers,
        )
        
        assert create_response.status_code == 201
        invoice_id = create_response.json()["id"]
        
        get_response = api_client.get(
            f"/invoices/{invoice_id}",
            headers=admin_headers,
        )
        
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["customer_id"] == customer_id
        assert data["status"] == "draft"
        assert data["notes"] == "Persistence test invoice"
        assert len(data["items"]) == 1

    def test_invoice_items_persist(
        self, api_client: httpx.Client, admin_headers: dict,
        test_customer_data: dict
    ):
        """Test that invoice items persist correctly."""
        import uuid
        
        customer_response = api_client.post(
            "/customers",
            json=test_customer_data,
            headers=admin_headers,
        )
        customer_id = customer_response.json()["id"]
        
        products = []
        for i in range(3):
            unique_id = str(uuid.uuid4())[:8]
            product_data = {
                "name": f"Persistence Product {i}",
                "price": (i + 1) * 25.00,
                "sku": f"PRS-{unique_id}",
            }
            response = api_client.post(
                "/products",
                json=product_data,
                headers=admin_headers,
            )
            products.append(response.json())
        
        invoice_data = {
            "customer_id": customer_id,
            "status": "draft",
            "tax_rate": 5,
            "items": [
                {
                    "product_id": p["id"],
                    "quantity": (i + 1) * 2,
                    "unit_price": p["price"],
                    "description": f"Item {i} description",
                }
                for i, p in enumerate(products)
            ],
        }
        
        create_response = api_client.post(
            "/invoices",
            json=invoice_data,
            headers=admin_headers,
        )
        invoice_id = create_response.json()["id"]
        
        get_response = api_client.get(
            f"/invoices/{invoice_id}",
            headers=admin_headers,
        )
        
        assert get_response.status_code == 200
        items = get_response.json()["items"]
        assert len(items) == 3
        
        for i, item in enumerate(items):
            assert item["product_id"] == products[i]["id"]
            assert item["quantity"] == (i + 1) * 2

    def test_user_data_persists_in_mongodb(
        self, api_client: httpx.Client, test_user_data: dict
    ):
        """Test that user data persists in MongoDB."""
        register_response = api_client.post(
            "/auth/register",
            json=test_user_data,
        )
        
        assert register_response.status_code == 201
        
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
        data = me_response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert data["role"] == test_user_data["role"]

    def test_role_update_persists(
        self, api_client: httpx.Client, admin_headers: dict,
        test_user_data: dict
    ):
        """Test that role updates persist in MongoDB."""
        register_response = api_client.post(
            "/auth/register",
            json=test_user_data,
        )
        user_id = register_response.json()["_id"]
        
        update_response = api_client.put(
            f"/auth/users/{user_id}",
            json={"role": "manager"},
            headers=admin_headers,
        )
        
        assert update_response.status_code == 200
        
        login_response = api_client.post(
            "/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        token = login_response.json()["access_token"]
        
        me_response = api_client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert me_response.json()["role"] == "manager"

    def test_deleted_data_does_not_persist(
        self, api_client: httpx.Client, admin_headers: dict,
        test_customer_data: dict
    ):
        """Test that deleted data is properly removed."""
        create_response = api_client.post(
            "/customers",
            json=test_customer_data,
            headers=admin_headers,
        )
        customer_id = create_response.json()["id"]
        
        delete_response = api_client.delete(
            f"/customers/{customer_id}",
            headers=admin_headers,
        )
        
        assert delete_response.status_code == 204
        
        get_response = api_client.get(
            f"/customers/{customer_id}",
            headers=admin_headers,
        )
        
        assert get_response.status_code == 404

    def test_list_endpoints_return_persisted_data(
        self, api_client: httpx.Client, admin_headers: dict,
        test_customer_data: dict, test_product_data: dict
    ):
        """Test that list endpoints return all persisted data."""
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
        
        customers_list = api_client.get(
            "/customers",
            headers=admin_headers,
        )
        assert customers_list.status_code == 200
        customer_ids = [c["id"] for c in customers_list.json()]
        assert customer_id in customer_ids
        
        products_list = api_client.get(
            "/products",
            headers=admin_headers,
        )
        assert products_list.status_code == 200
        product_ids = [p["id"] for p in products_list.json()]
        assert product_id in product_ids
