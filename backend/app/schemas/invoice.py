from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.postgres_models import InvoiceStatus


class InvoiceItemBase(BaseModel):
    product_id: int
    description: Optional[str] = None
    quantity: Decimal = Field(default=1, ge=0)
    unit_price: Decimal = Field(ge=0)


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemResponse(InvoiceItemBase):
    id: int
    subtotal: Decimal
    product_name: Optional[str] = None

    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    customer_id: int
    status: InvoiceStatus = InvoiceStatus.DRAFT
    due_date: Optional[datetime] = None
    tax_rate: Decimal = Field(default=0, ge=0, le=100)
    notes: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate] = []


class InvoiceUpdate(BaseModel):
    customer_id: Optional[int] = None
    status: Optional[InvoiceStatus] = None
    due_date: Optional[datetime] = None
    tax_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    notes: Optional[str] = None
    items: Optional[List[InvoiceItemCreate]] = None


class InvoiceResponse(InvoiceBase):
    id: int
    invoice_number: str
    issue_date: datetime
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    pdf_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: List[InvoiceItemResponse] = []
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None

    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    id: int
    invoice_number: str
    customer_id: int
    customer_name: Optional[str] = None
    status: InvoiceStatus
    issue_date: datetime
    due_date: Optional[datetime] = None
    total: Decimal

    class Config:
        from_attributes = True
