"""Quote schemas for validation."""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class QuoteBase(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    subtotal: float = Field(default=0.0, ge=0)
    tax_amount: float = Field(default=0.0, ge=0)
    discount_amount: float = Field(default=0.0, ge=0)
    total_amount: float = Field(default=0.0, ge=0)
    valid_until: date
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    notes: Optional[str] = None


class QuoteCreate(QuoteBase):
    customer_id: int
    opportunity_id: Optional[int] = None


class QuoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    status: Optional[str] = None
    subtotal: Optional[float] = Field(None, ge=0)
    tax_amount: Optional[float] = Field(None, ge=0)
    discount_amount: Optional[float] = Field(None, ge=0)
    total_amount: Optional[float] = Field(None, ge=0)
    valid_until: Optional[date] = None
    payment_terms: Optional[str] = None
    delivery_terms: Optional[str] = None
    notes: Optional[str] = None


class Quote(QuoteBase):
    id: int
    quote_number: str
    customer_id: int
    opportunity_id: Optional[int]
    created_by_id: int
    approved_by_id: Optional[int]
    status: str
    valid_from: date
    created_at: datetime
    updated_at: datetime
    approved_at: Optional[datetime]
    sent_at: Optional[datetime]

    class Config:
        from_attributes = True
