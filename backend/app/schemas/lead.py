"""Lead schemas for validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class LeadBase(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    source: str = "website"
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1)
    last_name: Optional[str] = Field(None, min_length=1)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    score: Optional[int] = Field(None, ge=0, le=100)
    notes: Optional[str] = None
    assigned_to_id: Optional[int] = None


class Lead(LeadBase):
    id: int
    status: str
    score: int
    assigned_to_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    qualified_at: Optional[datetime]
    converted_at: Optional[datetime]

    class Config:
        from_attributes = True
