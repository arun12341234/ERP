"""
Purchase Requisition model - internal purchase requests.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float, Date
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
from app.core.config import settings


class PRStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONVERTED_TO_PO = "converted_to_po"
    CANCELLED = "cancelled"


class PurchaseRequisition(Base):
    __tablename__ = "purchase_requisitions"

    id = Column(Integer, primary_key=True, index=True)
    pr_number = Column(String, unique=True, index=True, nullable=False)

    # Requester
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    department = Column(String, nullable=True)

    # Product/Item
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)

    # Purpose
    purpose = Column(Text, nullable=True)
    required_date = Column(Date, nullable=True)

    # Status
    status = Column(Enum(PRStatus), default=PRStatus.DRAFT, index=True)

    # Approval
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    product = relationship("Product")

    def __repr__(self):
        return f"<PurchaseRequisition {self.pr_number} - {self.status}>"
