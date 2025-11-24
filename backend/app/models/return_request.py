"""
Return Request model - returns and reverse logistics.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class ReturnRequestStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    COLLECTION_SCHEDULED = "collection_scheduled"
    IN_TRANSIT = "in_transit"
    RECEIVED = "received"
    INSPECTED = "inspected"
    REFUNDED = "refunded"
    RESTOCKED = "restocked"


class ReturnReason(str, enum.Enum):
    DEFECTIVE = "defective"
    WRONG_ITEM = "wrong_item"
    DAMAGED = "damaged"
    NOT_AS_DESCRIBED = "not_as_described"
    CUSTOMER_CHANGED_MIND = "customer_changed_mind"
    EXPIRED = "expired"
    OTHER = "other"


class ReturnRequest(Base):
    __tablename__ = "return_requests"

    id = Column(Integer, primary_key=True, index=True)
    return_number = Column(String, unique=True, index=True, nullable=False)

    # Original transaction
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)

    # Customer
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    # Product
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Return details
    request_date = Column(Date, nullable=False)
    return_reason = Column(Enum(ReturnReason), nullable=False)
    reason_description = Column(Text, nullable=True)

    # Quantity
    quantity_to_return = Column(Float, nullable=False)
    quantity_received = Column(Float, default=0.0)

    # Status
    status = Column(Enum(ReturnRequestStatus), default=ReturnRequestStatus.SUBMITTED)

    # Approval
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approval_date = Column(DateTime, nullable=True)
    approval_notes = Column(Text, nullable=True)

    # Collection
    collection_date = Column(Date, nullable=True)
    collection_address = Column(Text, nullable=True)

    # Inspection
    inspected_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    inspection_date = Column(DateTime, nullable=True)
    inspection_notes = Column(Text, nullable=True)
    condition_on_return = Column(String, nullable=True)

    # Refund (in cents)
    refund_amount = Column(Integer, default=0)
    refund_processed = Column(Integer, default=0)  # boolean as int

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    customer = relationship("Customer")
    product = relationship("Product")

    def __repr__(self):
        return f"<ReturnRequest {self.return_number}>"
