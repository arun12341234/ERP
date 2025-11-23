"""Feedback schemas for validation."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FeedbackBase(BaseModel):
    subject: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    category: str = "other"
    rating: Optional[int] = Field(None, ge=1, le=5)


class FeedbackCreate(FeedbackBase):
    customer_id: int


class FeedbackUpdate(BaseModel):
    status: Optional[str] = None
    response: Optional[str] = None


class Feedback(FeedbackBase):
    id: int
    customer_id: int
    status: str
    response: Optional[str]
    responded_by_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    responded_at: Optional[datetime]

    class Config:
        from_attributes = True
