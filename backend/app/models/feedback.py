"""
Feedback model - customer feedback logging and categorization.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
from app.core.config import settings


class FeedbackCategory(str, enum.Enum):
    PRODUCT = "product"
    SERVICE = "service"
    SUPPORT = "support"
    BILLING = "billing"
    FEATURE_REQUEST = "feature_request"
    OTHER = "other"


class FeedbackStatus(str, enum.Enum):
    NEW = "new"
    REVIEWED = "reviewed"
    ACTIONED = "actioned"
    CLOSED = "closed"


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)

    # Links
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    # Feedback details
    category = Column(Enum(FeedbackCategory), default=FeedbackCategory.OTHER)
    subject = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True)  # 1-5 stars

    # Status
    status = Column(Enum(FeedbackStatus), default=FeedbackStatus.NEW, index=True)
    response = Column(Text, nullable=True)
    responded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    responded_at = Column(DateTime, nullable=True)

    # Multi-tenant
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    customer = relationship("Customer", back_populates="feedback")
    responded_by = relationship("User", foreign_keys=[responded_by_id])

    def __repr__(self):
        return f"<Feedback {self.id} - {self.category} - {self.status}>"
