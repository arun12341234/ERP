"""
Quote/Quotation model - price quotes for customers.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float, Date, Boolean
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
from app.core.config import settings


class QuoteStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    SENT = "sent"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    quote_number = Column(String, unique=True, index=True, nullable=False)

    # Links
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Quote details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(QuoteStatus), default=QuoteStatus.DRAFT, index=True)

    # Financial
    subtotal = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)

    # Validity
    valid_from = Column(Date, default=date.today)
    valid_until = Column(Date, nullable=False)

    # Terms
    payment_terms = Column(String, nullable=True)
    delivery_terms = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)

    # Multi-tenant
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    customer = relationship("Customer", back_populates="quotes")
    opportunity = relationship("Opportunity", back_populates="quotes")
    created_by = relationship("User", foreign_keys=[created_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    sales_orders = relationship("SalesOrder", back_populates="quote")

    def __repr__(self):
        return f"<Quote {self.quote_number} - {self.status}>"
