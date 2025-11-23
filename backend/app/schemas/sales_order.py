"""Sales Order schemas for validation."""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class SalesOrderBase(BaseModel):
    subtotal: float = Field(default=0.0, ge=0)
    tax_amount: float = Field(default=0.0, ge=0)
    discount_amount: float = Field(default=0.0, ge=0)
    total_amount: float = Field(default=0.0, ge=0)
    delivery_address: Optional[str] = None
    requested_delivery_date: Optional[date] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None


class SalesOrderCreate(SalesOrderBase):
    customer_id: int
    quote_id: Optional[int] = None


class SalesOrderUpdate(BaseModel):
    status: Optional[str] = None
    subtotal: Optional[float] = Field(None, ge=0)
    tax_amount: Optional[float] = Field(None, ge=0)
    discount_amount: Optional[float] = Field(None, ge=0)
    total_amount: Optional[float] = Field(None, ge=0)
    delivery_address: Optional[str] = None
    requested_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    credit_check_status: Optional[str] = None
    credit_check_notes: Optional[str] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None


class SalesOrder(SalesOrderBase):
    id: int
    order_number: str
    customer_id: int
    quote_id: Optional[int]
    created_by_id: int
    status: str
    credit_check_status: Optional[str]
    actual_delivery_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime]
    shipped_at: Optional[datetime]
    delivered_at: Optional[datetime]

    class Config:
        from_attributes = True
