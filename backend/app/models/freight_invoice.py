"""
Freight Invoice model - freight billing and verification.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class FreightInvoiceStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    APPROVED = "approved"
    PAID = "paid"
    DISPUTED = "disputed"


class FreightInvoice(Base):
    __tablename__ = "freight_invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, unique=True, index=True, nullable=False)

    # Shipment reference
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=True)
    logistics_request_id = Column(Integer, ForeignKey("logistics_requests.id"), nullable=True)

    # Carrier
    carrier_name = Column(String, nullable=False)
    carrier_invoice_number = Column(String, nullable=True)

    # Invoice details
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)

    # Amounts (in cents)
    base_freight_charge = Column(Integer, nullable=False)
    fuel_surcharge = Column(Integer, default=0)
    handling_charges = Column(Integer, default=0)
    insurance_charges = Column(Integer, default=0)
    other_charges = Column(Integer, default=0)
    tax_amount = Column(Integer, default=0)
    total_amount = Column(Integer, nullable=False)

    # Status
    status = Column(Enum(FreightInvoiceStatus), default=FreightInvoiceStatus.PENDING)

    # Verification
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_date = Column(DateTime, nullable=True)
    verification_notes = Column(Text, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<FreightInvoice {self.invoice_number}>"
