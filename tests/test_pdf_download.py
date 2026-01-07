"""
E2E Tests for PDF Download
Tests the PDF invoice generation and download functionality.
"""
import pytest
import httpx


class TestPdfDownload:
    """Test suite for PDF download functionality."""

    @pytest.fixture
    def created_invoice(
        self, api_client: httpx.Client, admin_headers: dict,
        test_customer_data: dict, test_product_data: dict
    ) -> dict:
        """Create an invoice for PDF testing."""
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
        
        invoice_data = {
            "customer_id": customer["id"],
            "status": "pending",
            "tax_rate": 10,
            "notes": "Test invoice for PDF generation",
            "items": [
                {
                    "product_id": product["id"],
                    "quantity": 2,
                    "unit_price": product["price"],
                    "description": "Test product item",
                }
            ],
        }
        
        response = api_client.post(
            "/invoices",
            json=invoice_data,
            headers=admin_headers,
        )
        return response.json()

    def test_download_invoice_pdf_success(
        self, api_client: httpx.Client, admin_headers: dict,
        created_invoice: dict
    ):
        """Test successful PDF download."""
        response = api_client.get(
            f"/invoices/{created_invoice['id']}/pdf",
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers.get("content-disposition", "")
        assert created_invoice["invoice_number"] in response.headers.get(
            "content-disposition", ""
        )

    def test_pdf_contains_valid_content(
        self, api_client: httpx.Client, admin_headers: dict,
        created_invoice: dict
    ):
        """Test that PDF contains valid PDF content."""
        response = api_client.get(
            f"/invoices/{created_invoice['id']}/pdf",
            headers=admin_headers,
        )
        
        assert response.status_code == 200
        
        pdf_content = response.content
        assert pdf_content.startswith(b"%PDF")
        assert len(pdf_content) > 1000

    def test_download_pdf_nonexistent_invoice_fails(
        self, api_client: httpx.Client, admin_headers: dict
    ):
        """Test that downloading PDF for non-existent invoice fails."""
        response = api_client.get(
            "/invoices/99999/pdf",
            headers=admin_headers,
        )
        
        assert response.status_code == 404

    def test_download_pdf_without_auth_fails(
        self, api_client: httpx.Client, created_invoice: dict
    ):
        """Test that downloading PDF without authentication fails."""
        response = api_client.get(f"/invoices/{created_invoice['id']}/pdf")
        
        assert response.status_code in [401, 403]

    def test_viewer_can_download_pdf(
        self, api_client: httpx.Client, created_invoice: dict
    ):
        """Test that viewer role can download PDF."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        viewer_data = {
            "username": f"viewer_{unique_id}",
            "email": f"viewer_{unique_id}@test.com",
            "password": "TestPassword123!",
            "role": "viewer",
        }
        api_client.post("/auth/register", json=viewer_data)
        login_response = api_client.post(
            "/auth/login",
            json={"email": viewer_data["email"], "password": viewer_data["password"]},
        )
        viewer_token = login_response.json()["access_token"]
        
        response = api_client.get(
            f"/invoices/{created_invoice['id']}/pdf",
            headers={"Authorization": f"Bearer {viewer_token}"},
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"

    def test_pdf_generated_on_invoice_creation(
        self, api_client: httpx.Client, admin_headers: dict,
        test_customer_data: dict, test_product_data: dict
    ):
        """Test that PDF is auto-generated when invoice is created."""
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
        
        invoice_data = {
            "customer_id": customer["id"],
            "status": "draft",
            "tax_rate": 5,
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
        
        assert create_response.status_code == 201
        invoice = create_response.json()
        
        pdf_response = api_client.get(
            f"/invoices/{invoice['id']}/pdf",
            headers=admin_headers,
        )
        
        assert pdf_response.status_code == 200
        assert pdf_response.headers["content-type"] == "application/pdf"

    def test_pdf_reflects_invoice_data(
        self, api_client: httpx.Client, admin_headers: dict,
        created_invoice: dict
    ):
        """Test that PDF can be downloaded for invoices with different statuses."""
        for status in ["draft", "pending", "paid"]:
            api_client.put(
                f"/invoices/{created_invoice['id']}",
                json={"status": status},
                headers=admin_headers,
            )
            
            response = api_client.get(
                f"/invoices/{created_invoice['id']}/pdf",
                headers=admin_headers,
            )
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/pdf"
