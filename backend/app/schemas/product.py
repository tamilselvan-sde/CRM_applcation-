from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    sku: Optional[str] = Field(None, max_length=100)
    price: Decimal = Field(ge=0)
    unit: str = Field(default="unit", max_length=50)
    is_service: bool = False
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    sku: Optional[str] = Field(None, max_length=100)
    price: Optional[Decimal] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=50)
    is_service: Optional[bool] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
