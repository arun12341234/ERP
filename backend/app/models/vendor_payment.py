"""
Vendor Payment model - accounts payable payment processing.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PROCESSED = "processed"
    CLEARED = "cleared"
    REJECTED = "rejected"


class PaymentMethod(str, enum.Enum):
    BANK_TRANSFER = "bank_transfer"
    CHECK = "check"
    CASH = "cash"
    CARD = "card"
    ACH = "ach"
    WIRE = "wire"


class VendorPayment(Base):
    __tablename__ = "vendor_payments"

    id = Column(Integer, primary_key=True, index=True)
    payment_number = Column(String, unique=True, index=True, nullable=False)

    # Vendor
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)

    # Payment details
    payment_date = Column(Date, nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    reference_number = Column(String, nullable=True)  # Check number, transaction ID, etc.

    # Amount (in cents)
    payment_amount = Column(Integer, nullable=False)

    # Bank account
    bank_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True)

    # Status
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)

    # Approvals
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approval_date = Column(DateTime, nullable=True)

    # Processing
    processed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    processed_date = Column(DateTime, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    vendor = relationship("Vendor")

    def __repr__(self):
        return f"<VendorPayment {self.payment_number}>"
