"""
Invoice model - customer invoices.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, unique=True, index=True, nullable=False)

    # Customer
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    # Sales order reference (optional)
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=True)

    # Invoice details
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    payment_terms = Column(String, nullable=True)  # e.g., "Net 30"

    # Amounts (in cents to avoid float precision issues)
    subtotal = Column(Integer, default=0)
    tax_amount = Column(Integer, default=0)
    discount_amount = Column(Integer, default=0)
    total_amount = Column(Integer, default=0)
    amount_paid = Column(Integer, default=0)
    amount_due = Column(Integer, default=0)

    # Status
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)

    # Notes
    notes = Column(Text, nullable=True)
    terms_conditions = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    customer = relationship("Customer")

    def __repr__(self):
        return f"<Invoice {self.invoice_number}>"
