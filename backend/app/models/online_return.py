"""
Online Return model - e-commerce returns booking and processing.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class OnlineReturnStatus(str, enum.Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    REJECTED = "rejected"
    PICKUP_SCHEDULED = "pickup_scheduled"
    IN_TRANSIT = "in_transit"
    RECEIVED = "received"
    INSPECTED = "inspected"
    REFUNDED = "refunded"
    EXCHANGE_INITIATED = "exchange_initiated"
    COMPLETED = "completed"


class OnlineReturnReason(str, enum.Enum):
    DEFECTIVE = "defective"
    WRONG_ITEM = "wrong_item"
    DAMAGED = "damaged"
    SIZE_ISSUE = "size_issue"
    COLOR_MISMATCH = "color_mismatch"
    NOT_AS_DESCRIBED = "not_as_described"
    CHANGED_MIND = "changed_mind"
    QUALITY_ISSUE = "quality_issue"
    OTHER = "other"


class RefundMethod(str, enum.Enum):
    ORIGINAL_PAYMENT = "original_payment"
    WALLET = "wallet"
    BANK_TRANSFER = "bank_transfer"
    STORE_CREDIT = "store_credit"


class OnlineReturn(Base):
    __tablename__ = "online_returns"

    id = Column(Integer, primary_key=True, index=True)
    return_number = Column(String, unique=True, index=True, nullable=False)

    # Order reference
    online_order_id = Column(Integer, ForeignKey("online_orders.id"), nullable=False)
    order_number = Column(String, nullable=False, index=True)

    # Customer
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    # Return details
    request_date = Column(Date, nullable=False)
    return_reason = Column(Enum(OnlineReturnReason), nullable=False)
    reason_description = Column(Text, nullable=True)

    # Items to return (JSON array)
    items = Column(Text, nullable=False)  # [{sku, quantity, reason}]

    # Quantities
    total_quantity = Column(Float, nullable=False)
    quantity_received = Column(Float, default=0.0)

    # Status
    status = Column(Enum(OnlineReturnStatus), default=OnlineReturnStatus.REQUESTED)

    # Approval
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approval_date = Column(DateTime, nullable=True)
    approval_notes = Column(Text, nullable=True)

    # Pickup/Collection
    pickup_date = Column(Date, nullable=True)
    pickup_address = Column(Text, nullable=True)
    pickup_tracking_number = Column(String, nullable=True)

    # Inspection
    inspected_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    inspection_date = Column(DateTime, nullable=True)
    inspection_notes = Column(Text, nullable=True)
    condition_on_return = Column(String, nullable=True)

    # Refund details
    refund_method = Column(Enum(RefundMethod), nullable=True)
    refund_amount = Column(Integer, default=0)  # in cents
    refund_processed = Column(Integer, default=0)  # boolean as int
    refund_transaction_id = Column(String, nullable=True)
    refunded_at = Column(DateTime, nullable=True)

    # Exchange (if applicable)
    is_exchange = Column(Integer, default=0)  # boolean as int
    exchange_order_id = Column(Integer, ForeignKey("online_orders.id"), nullable=True)

    # Images/Proof
    images = Column(Text, nullable=True)  # JSON array of URLs

    # Notes
    customer_notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    customer = relationship("Customer")

    def __repr__(self):
        return f"<OnlineReturn {self.return_number}>"
