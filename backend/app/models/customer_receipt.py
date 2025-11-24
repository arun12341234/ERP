"""
Customer Receipt model - accounts receivable receipt processing.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class ReceiptStatus(str, enum.Enum):
    PENDING = "pending"
    RECORDED = "recorded"
    CLEARED = "cleared"
    BOUNCED = "bounced"


class ReceiptMethod(str, enum.Enum):
    BANK_TRANSFER = "bank_transfer"
    CHECK = "check"
    CASH = "cash"
    CARD = "card"
    ACH = "ach"
    WIRE = "wire"


class CustomerReceipt(Base):
    __tablename__ = "customer_receipts"

    id = Column(Integer, primary_key=True, index=True)
    receipt_number = Column(String, unique=True, index=True, nullable=False)

    # Customer
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    # Invoice reference (optional)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)

    # Receipt details
    receipt_date = Column(Date, nullable=False)
    receipt_method = Column(Enum(ReceiptMethod), nullable=False)
    reference_number = Column(String, nullable=True)  # Check number, transaction ID, etc.

    # Amount (in cents)
    receipt_amount = Column(Integer, nullable=False)

    # Bank account
    bank_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True)

    # Status
    status = Column(Enum(ReceiptStatus), default=ReceiptStatus.PENDING)

    # Recorded by
    recorded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    recorded_date = Column(DateTime, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    customer = relationship("Customer")
    invoice = relationship("Invoice")

    def __repr__(self):
        return f"<CustomerReceipt {self.receipt_number}>"
