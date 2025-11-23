"""Opportunity schemas for validation."""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field


class OpportunityBase(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    amount: float = Field(default=0.0, ge=0)
    probability: int = Field(default=10, ge=0, le=100)
    expected_close_date: Optional[date] = None


class OpportunityCreate(OpportunityBase):
    lead_id: Optional[int] = None
    customer_id: Optional[int] = None
    assigned_to_id: int


class OpportunityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    stage: Optional[str] = None
    probability: Optional[int] = Field(None, ge=0, le=100)
    amount: Optional[float] = Field(None, ge=0)
    expected_close_date: Optional[date] = None
    assigned_to_id: Optional[int] = None


class Opportunity(OpportunityBase):
    id: int
    lead_id: Optional[int]
    customer_id: Optional[int]
    assigned_to_id: int
    stage: str
    score: int
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime]

    class Config:
        from_attributes = True
