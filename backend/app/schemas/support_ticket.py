"""Support Ticket schemas for validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SupportTicketBase(BaseModel):
    subject: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    category: str = "general"
    priority: str = "medium"


class SupportTicketCreate(SupportTicketBase):
    customer_id: int


class SupportTicketUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to_id: Optional[int] = None
    resolution_notes: Optional[str] = None
    escalation_reason: Optional[str] = None
    escalated_to_id: Optional[int] = None


class SupportTicket(SupportTicketBase):
    id: int
    ticket_number: str
    customer_id: int
    assigned_to_id: Optional[int]
    status: str
    resolution_notes: Optional[str]
    resolved_by_id: Optional[int]
    is_escalated: bool
    escalated_to_id: Optional[int]
    escalation_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    closed_at: Optional[datetime]
    escalated_at: Optional[datetime]

    class Config:
        from_attributes = True
