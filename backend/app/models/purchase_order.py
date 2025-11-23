"""
Purchase Order model - orders to vendors.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float, Date, Boolean
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
from app.core.config import settings


class POStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SENT_TO_VENDOR = "sent_to_vendor"
    PARTIALLY_RECEIVED = "partially_received"
    FULLY_RECEIVED = "fully_received"
    CANCELLED = "cancelled"


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String, unique=True, index=True, nullable=False)

    # Vendor
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)

    # Links
    pr_id = Column(Integer, ForeignKey("purchase_requisitions.id"), nullable=True)

    # Product
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)

    # Delivery
    expected_delivery_date = Column(Date, nullable=True)
    delivery_address = Column(Text, nullable=True)

    # Status
    status = Column(Enum(POStatus), default=POStatus.DRAFT, index=True)

    # Approval
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)

    # Terms
    payment_terms = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    vendor = relationship("Vendor", back_populates="purchase_orders")
    product = relationship("Product")
    created_by = relationship("User", foreign_keys=[created_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    grns = relationship("GoodsReceiptNote", back_populates="purchase_order")

    def __repr__(self):
        return f"<PurchaseOrder {self.po_number} - {self.status}>"
