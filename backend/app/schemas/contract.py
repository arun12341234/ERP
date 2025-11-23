"""Contract schemas for validation."""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class ContractBase(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    contract_type: str = "service"
    value: float = Field(default=0.0, ge=0)
    billing_frequency: Optional[str] = None
    start_date: date
    end_date: date
    auto_renew: bool = False
    payment_terms: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    notes: Optional[str] = None


class ContractCreate(ContractBase):
    customer_id: int


class ContractUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    status: Optional[str] = None
    value: Optional[float] = Field(None, ge=0)
    billing_frequency: Optional[str] = None
    end_date: Optional[date] = None
    renewal_date: Optional[date] = None
    auto_renew: Optional[bool] = None
    payment_terms: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    notes: Optional[str] = None


class Contract(ContractBase):
    id: int
    contract_number: str
    customer_id: int
    created_by_id: int
    status: str
    renewal_date: Optional[date]
    renewal_notified: bool
    renewal_notified_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    activated_at: Optional[datetime]
    renewed_at: Optional[datetime]

    class Config:
        from_attributes = True
