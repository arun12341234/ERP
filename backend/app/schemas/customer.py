"""Customer schemas for validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    phone: Optional[str] = None
    customer_type: str = "individual"
    company_name: Optional[str] = None
    tax_id: Optional[str] = None
    billing_address: Optional[str] = None
    shipping_address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    credit_limit: float = 0.0
    payment_terms: Optional[str] = None


class CustomerCreate(CustomerBase):
    user_id: Optional[int] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    customer_type: Optional[str] = None
    company_name: Optional[str] = None
    tax_id: Optional[str] = None
    billing_address: Optional[str] = None
    shipping_address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    credit_limit: Optional[float] = None
    payment_terms: Optional[str] = None
    status: Optional[str] = None


class Customer(CustomerBase):
    id: int
    user_id: Optional[int]
    status: str
    current_balance: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
