"""
Goods Receipt Note (GRN) model - receiving goods from vendors.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Date, Enum, Boolean
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
from app.core.config import settings


class GRNStatus(str, enum.Enum):
    PENDING = "pending"
    INSPECTED = "inspected"
    PUT_AWAY = "put_away"
    REJECTED = "rejected"


class GoodsReceiptNote(Base):
    __tablename__ = "goods_receipt_notes"

    id = Column(Integer, primary_key=True, index=True)
    grn_number = Column(String, unique=True, index=True, nullable=False)

    # PO reference
    po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)

    # Receipt details
    received_date = Column(Date, default=date.today)
    received_quantity = Column(Float, nullable=False)

    # Inspection
    status = Column(Enum(GRNStatus), default=GRNStatus.PENDING)
    quality_check_passed = Column(Boolean, nullable=True)

    # Personnel
    received_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Documents
    delivery_note_number = Column(String, nullable=True)
    invoice_number = Column(String, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="grns")
    received_by = relationship("User")
    quality_inspections = relationship("QualityInspection", back_populates="grn")

    def __repr__(self):
        return f"<GRN {self.grn_number} - {self.status}>"
