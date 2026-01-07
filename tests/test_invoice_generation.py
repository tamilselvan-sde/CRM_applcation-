"""
E2E Tests for Invoice Generation
Tests the complete invoice creation and management flow.
"""
import pytest
import httpx


class TestInvoiceGeneration:
    """Test suite for invoice generation functionality."""

    @pytest.fixture
    def setup_customer_and_product(
        self, api_client: httpx.Client, admin_headers: dict,
        test_customer_data: dict, test_product_data: dict
    ) -> tuple:
        """Create a customer and product for invoice testing."""
        customer_response = api_client.post(
            "/customers",
            json=test_customer_data,
            headers=admin_headers,
        )
        customer = customer_response.json()
        
        product_response = api_client.post(
            "/products",
            json=test_product_data,
            headers=admin_headers,
        )
        product = product_response.json()
        
        return customer, product

    def test_create_invoice_success(
        self, api_client: httpx.Client, admin_headers: dict,
        setup_customer_and_product: tuple
    ):
        """Test successful invoice creation."""
        customer, product = setup_customer_and_product
        
        invoice_data = {
            "customer_id": customer["id"],
            "status": "draft",
            "tax_rate": 10,
            "notes": "Test invoice",
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": 2,
                    "unit_price": product["price"],
                    "description": "Test item",
                }
            ],
        }
        
        response = api_client.post(
            "/invoices",
            json=invoice_data,
            headers=admin_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["customer_id"] == customer["id"]
        assert data["status"] == "draft"
        assert len(data["items"]) == 1
        assert "invoice_number" in data
        assert data["invoice_number"].startswith("INV-")

    def test_invoice_calculates_totals_correctly(
        self, api_client: httpx.Client, admin_headers: dict,
        setup_customer_and_product: tuple
    ):
        """Test that invoice totals are calculated correctly."""
        customer, product = setup_customer_and_product
        
        quantity = 3
        unit_price = 100.00
        tax_rate = 10
        
        invoice_data = {
            "customer_id": customer["id"],
            "status": "draft",
            "tax_rate": tax_rate,
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": quantity,
                    "unit_price": unit_price,
                }
            ],
        }
        
        response = api_client.post(
            "/invoices",
            json=invoice_data,
            headers=admin_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        
        expected_subtotal = quantity * unit_price
        expected_tax = expected_subtotal * (tax_rate / 100)
        expected_total = expected_subtotal + expected_tax
        
        assert float(data["subtotal"]) == expected_subtotal
        assert float(data["tax_amount"]) == expected_tax
        assert float(data["total"]) == expected_total

    def test_create_invoice_with_multiple_items(
        self, api_client: httpx.Client, admin_headers: dict,
        test_customer_data: dict
    ):
        """Test creating invoice with multiple line items."""
        import uuid
        
        customer_response = api_client.post(
            "/customers",
            json=test_customer_data,
            headers=admin_headers,
        )
        customer = customer_response.json()
        
        products = []
        for i in range(3):
            unique_id = str(uuid.uuid4())[:8]
            product_data = {
                "name": f"Product {i}",
                "price": (i + 1) * 50.00,
                "sku": f"PRD-{unique_id}",
            }
            response = api_client.post(
                "/products",
                json=product_data,
                headers=admin_headers,
            )
            products.append(response.json())
        
        invoice_data = {
            "customer_id": customer["id"],
            "status": "draft",
            "tax_rate": 5,
            "items": [
                {
                    "product_id": p["id"],
                    "quantity": i + 1,
                    "unit_price": p["price"],
                }
                for i, p in enumerate(products)
            ],
        }
        
        response = api_client.post(
            "/invoices",
            json=invoice_data,
            headers=admin_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert len(data["items"]) == 3

    def test_get_invoice_by_id(
        self, api_client: httpx.Client, admin_headers: dict,
        setup_customer_and_product: tuple
    ):
        """Test retrieving invoice by ID."""
        customer, product = setup_customer_and_product
        
        invoice_data = {
            "customer_id": customer["id"],
            "status": "draft",
            "tax_rate": 10,
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": 1,
                    "unit_price": product["price"],
                }
            ],
        }
        
        create_response = api_client.post(
            "/invoices",
            json=invoice_data,
            headers=admin_headers,
        )
        invoice_id = create_response.json()["id"]
        
        response = api_client.get(
            f"/invoices/{invoice_id}",
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == invoice_id
        assert data["customer_name"] == customer["name"]

    def test_update_invoice_status(
        self, api_client: httpx.Client, admin_headers: dict,
        setup_customer_and_product: tuple
    ):
        """Test updating invoice status."""
        customer, product = setup_customer_and_product
        
        invoice_data = {
            "customer_id": customer["id"],
            "status": "draft",
            "tax_rate": 10,
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": 1,
                    "unit_price": product["price"],
                }
            ],
        }
        
        create_response = api_client.post(
            "/invoices",
            json=invoice_data,
            headers=admin_headers,
        )
        invoice_id = create_response.json()["id"]
        
        response = api_client.put(
            f"/invoices/{invoice_id}",
            json={"status": "pending"},
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "pending"
        
        response = api_client.put(
            f"/invoices/{invoice_id}",
            json={"status": "paid"},
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "paid"

    def test_delete_invoice(
        self, api_client: httpx.Client, admin_headers: dict,
        setup_customer_and_product: tuple
    ):
        """Test deleting an invoice."""
        customer, product = setup_customer_and_product
        
        invoice_data = {
            "customer_id": customer["id"],
            "status": "draft",
            "tax_rate": 10,
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": 1,
                    "unit_price": product["price"],
                }
            ],
        }
        
        create_response = api_client.post(
            "/invoices",
            json=invoice_data,
            headers=admin_headers,
        )
        invoice_id = create_response.json()["id"]
        
        delete_response = api_client.delete(
            f"/invoices/{invoice_id}",
            headers=admin_headers,
        )
        
        assert delete_response.status_code == 204
        
        get_response = api_client.get(
            f"/invoices/{invoice_id}",
            headers=admin_headers,
        )
        
        assert get_response.status_code == 404

    def test_list_invoices_with_status_filter(
        self, api_client: httpx.Client, admin_headers: dict,
        setup_customer_and_product: tuple
    ):
        """Test listing invoices with status filter."""
        customer, product = setup_customer_and_product
        
        for status in ["draft", "pending", "paid"]:
            invoice_data = {
                "customer_id": customer["id"],
                "status": status,
                "tax_rate": 10,
                "items": [
                    {
                        "product_id": product["id"],
                        "quantity": 1,
                        "unit_price": product["price"],
                    }
                ],
            }
            api_client.post(
                "/invoices",
                json=invoice_data,
                headers=admin_headers,
            )
        
        response = api_client.get(
            "/invoices",
            params={"status": "paid"},
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(inv["status"] == "paid" for inv in data)

    def test_create_invoice_invalid_customer_fails(
        self, api_client: httpx.Client, admin_headers: dict,
        test_product_data: dict
    ):
        """Test that creating invoice with invalid customer fails."""
        product_response = api_client.post(
            "/products",
            json=test_product_data,
            headers=admin_headers,
        )
        product = product_response.json()
        
        invoice_data = {
            "customer_id": 99999,
            "status": "draft",
            "tax_rate": 10,
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": 1,
                    "unit_price": product["price"],
                }
            ],
        }
        
        response = api_client.post(
            "/invoices",
            json=invoice_data,
            headers=admin_headers,
        )
        
        assert response.status_code == 400
        assert "customer" in response.json()["detail"].lower()
