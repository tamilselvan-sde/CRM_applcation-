import logging
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database.postgres import get_db
from app.middleware.auth_middleware import require_permission
from app.models.postgres_models import Customer, Invoice, InvoiceItem, InvoiceStatus, Product
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceItemResponse,
    InvoiceListResponse,
    InvoiceResponse,
    InvoiceUpdate,
)
from app.schemas.user import TokenData
from app.services.pdf_service import generate_invoice_pdf, save_invoice_pdf

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/invoices", tags=["Invoices"])


def generate_invoice_number() -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"INV-{timestamp}"


def calculate_invoice_totals(
    items: List[InvoiceItem],
    tax_rate: Decimal,
) -> tuple[Decimal, Decimal, Decimal]:
    subtotal = sum(item.subtotal for item in items)
    tax_amount = subtotal * (tax_rate / 100)
    total = subtotal + tax_amount
    return subtotal, tax_amount, total


@router.get("", response_model=List[InvoiceListResponse])
async def get_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: InvoiceStatus = Query(None, alias="status"),
    customer_id: int = Query(None),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission("invoices:read")),
) -> List[InvoiceListResponse]:
    logger.info(f"Fetching invoices (skip={skip}, limit={limit})")

    query = db.query(Invoice).join(Customer)

    if status_filter:
        query = query.filter(Invoice.status == status_filter)

    if customer_id:
        query = query.filter(Invoice.customer_id == customer_id)

    invoices = query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for inv in invoices:
        result.append(InvoiceListResponse(
            id=inv.id,
            invoice_number=inv.invoice_number,
            customer_id=inv.customer_id,
            customer_name=inv.customer.name if inv.customer else None,
            status=inv.status,
            issue_date=inv.issue_date,
            due_date=inv.due_date,
            total=inv.total,
        ))

    return result


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission("invoices:read")),
) -> InvoiceResponse:
    logger.info(f"Fetching invoice: {invoice_id}")

    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    items_response = []
    for item in invoice.items:
        items_response.append(InvoiceItemResponse(
            id=item.id,
            product_id=item.product_id,
            description=item.description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=item.subtotal,
            product_name=item.product.name if item.product else None,
        ))

    return InvoiceResponse(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        customer_id=invoice.customer_id,
        status=invoice.status,
        issue_date=invoice.issue_date,
        due_date=invoice.due_date,
        subtotal=invoice.subtotal,
        tax_rate=invoice.tax_rate,
        tax_amount=invoice.tax_amount,
        total=invoice.total,
        notes=invoice.notes,
        pdf_path=invoice.pdf_path,
        created_at=invoice.created_at,
        updated_at=invoice.updated_at,
        items=items_response,
        customer_name=invoice.customer.name if invoice.customer else None,
        customer_email=invoice.customer.email if invoice.customer else None,
    )


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission("invoices:write")),
) -> InvoiceResponse:
    logger.info(f"Creating invoice for customer: {invoice_data.customer_id}")

    customer = db.query(Customer).filter(Customer.id == invoice_data.customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer not found",
        )

    invoice_number = generate_invoice_number()

    invoice = Invoice(
        invoice_number=invoice_number,
        customer_id=invoice_data.customer_id,
        status=invoice_data.status,
        due_date=invoice_data.due_date,
        tax_rate=invoice_data.tax_rate,
        notes=invoice_data.notes,
    )
    db.add(invoice)
    db.flush()

    for item_data in invoice_data.items:
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {item_data.product_id} not found",
            )

        item_subtotal = item_data.quantity * item_data.unit_price

        invoice_item = InvoiceItem(
            invoice_id=invoice.id,
            product_id=item_data.product_id,
            description=item_data.description or product.name,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            subtotal=item_subtotal,
        )
        db.add(invoice_item)

    db.flush()

    subtotal, tax_amount, total = calculate_invoice_totals(
        invoice.items, invoice.tax_rate
    )
    invoice.subtotal = subtotal
    invoice.tax_amount = tax_amount
    invoice.total = total

    db.commit()
    db.refresh(invoice)

    try:
        customer_address = "\n".join(filter(None, [
            customer.address,
            f"{customer.city}, {customer.state} {customer.postal_code}".strip(", "),
            customer.country,
        ]))

        items_for_pdf = [
            {
                "description": item.description or item.product.name,
                "product_name": item.product.name if item.product else "Item",
                "quantity": float(item.quantity),
                "unit_price": float(item.unit_price),
                "subtotal": float(item.subtotal),
            }
            for item in invoice.items
        ]

        pdf_bytes = generate_invoice_pdf(
            invoice_number=invoice.invoice_number,
            customer_name=customer.name,
            customer_email=customer.email,
            customer_address=customer_address if customer_address.strip() else None,
            issue_date=invoice.issue_date,
            due_date=invoice.due_date,
            items=items_for_pdf,
            subtotal=invoice.subtotal,
            tax_rate=invoice.tax_rate,
            tax_amount=invoice.tax_amount,
            total=invoice.total,
            notes=invoice.notes,
        )

        pdf_path = save_invoice_pdf(invoice.invoice_number, pdf_bytes)
        invoice.pdf_path = pdf_path
        db.commit()
        db.refresh(invoice)

    except Exception as e:
        logger.error(f"Failed to generate PDF for invoice {invoice.invoice_number}: {e}")

    logger.info(f"Invoice created: {invoice.id}")

    items_response = []
    for item in invoice.items:
        items_response.append(InvoiceItemResponse(
            id=item.id,
            product_id=item.product_id,
            description=item.description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=item.subtotal,
            product_name=item.product.name if item.product else None,
        ))

    return InvoiceResponse(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        customer_id=invoice.customer_id,
        status=invoice.status,
        issue_date=invoice.issue_date,
        due_date=invoice.due_date,
        subtotal=invoice.subtotal,
        tax_rate=invoice.tax_rate,
        tax_amount=invoice.tax_amount,
        total=invoice.total,
        notes=invoice.notes,
        pdf_path=invoice.pdf_path,
        created_at=invoice.created_at,
        updated_at=invoice.updated_at,
        items=items_response,
        customer_name=customer.name,
        customer_email=customer.email,
    )


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: int,
    invoice_update: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission("invoices:write")),
) -> InvoiceResponse:
    logger.info(f"Updating invoice: {invoice_id}")

    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    update_data = invoice_update.model_dump(exclude_unset=True)

    if "customer_id" in update_data:
        customer = db.query(Customer).filter(
            Customer.id == update_data["customer_id"]
        ).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer not found",
            )

    if "items" in update_data:
        for item in invoice.items:
            db.delete(item)

        for item_data in update_data["items"]:
            product = db.query(Product).filter(
                Product.id == item_data["product_id"]
            ).first()
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product {item_data['product_id']} not found",
                )

            quantity = Decimal(str(item_data["quantity"]))
            unit_price = Decimal(str(item_data["unit_price"]))
            item_subtotal = quantity * unit_price

            invoice_item = InvoiceItem(
                invoice_id=invoice.id,
                product_id=item_data["product_id"],
                description=item_data.get("description") or product.name,
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
                subtotal=item_subtotal,
            )
            db.add(invoice_item)

        del update_data["items"]

    for field, value in update_data.items():
        setattr(invoice, field, value)

    db.flush()

    subtotal, tax_amount, total = calculate_invoice_totals(
        invoice.items, invoice.tax_rate
    )
    invoice.subtotal = subtotal
    invoice.tax_amount = tax_amount
    invoice.total = total

    db.commit()
    db.refresh(invoice)

    logger.info(f"Invoice updated: {invoice_id}")

    items_response = []
    for item in invoice.items:
        items_response.append(InvoiceItemResponse(
            id=item.id,
            product_id=item.product_id,
            description=item.description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            subtotal=item.subtotal,
            product_name=item.product.name if item.product else None,
        ))

    return InvoiceResponse(
        id=invoice.id,
        invoice_number=invoice.invoice_number,
        customer_id=invoice.customer_id,
        status=invoice.status,
        issue_date=invoice.issue_date,
        due_date=invoice.due_date,
        subtotal=invoice.subtotal,
        tax_rate=invoice.tax_rate,
        tax_amount=invoice.tax_amount,
        total=invoice.total,
        notes=invoice.notes,
        pdf_path=invoice.pdf_path,
        created_at=invoice.created_at,
        updated_at=invoice.updated_at,
        items=items_response,
        customer_name=invoice.customer.name if invoice.customer else None,
        customer_email=invoice.customer.email if invoice.customer else None,
    )


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission("invoices:delete")),
) -> None:
    logger.info(f"Deleting invoice: {invoice_id}")

    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    db.delete(invoice)
    db.commit()

    logger.info(f"Invoice deleted: {invoice_id}")


@router.get("/{invoice_id}/pdf")
async def download_invoice_pdf(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_permission("invoices:read")),
) -> StreamingResponse:
    logger.info(f"Downloading PDF for invoice: {invoice_id}")

    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )

    customer = invoice.customer

    address_parts = []
    if customer:
        if customer.address:
            address_parts.append(customer.address)
        city_state_zip = f"{customer.city}, {customer.state} {customer.postal_code}"
        if city_state_zip.strip(", "):
            address_parts.append(city_state_zip.strip(", "))
        if customer.country:
            address_parts.append(customer.country)
    customer_address = "\n".join(address_parts)

    items_for_pdf = [
        {
            "description": item.description or (item.product.name if item.product else "Item"),
            "product_name": item.product.name if item.product else "Item",
            "quantity": float(item.quantity),
            "unit_price": float(item.unit_price),
            "subtotal": float(item.subtotal),
        }
        for item in invoice.items
    ]

    pdf_bytes = generate_invoice_pdf(
        invoice_number=invoice.invoice_number,
        customer_name=customer.name if customer else "Unknown",
        customer_email=customer.email if customer else "",
        customer_address=customer_address if customer_address.strip() else None,
        issue_date=invoice.issue_date,
        due_date=invoice.due_date,
        items=items_for_pdf,
        subtotal=invoice.subtotal,
        tax_rate=invoice.tax_rate,
        tax_amount=invoice.tax_amount,
        total=invoice.total,
        notes=invoice.notes,
    )

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=invoice_{invoice.invoice_number}.pdf"
        },
    )
