"""
Sales Order model - confirmed customer orders from quotes.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float, Date, Boolean
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
from app.core.config import settings


class SalesOrderStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_CREDIT_CHECK = "pending_credit_check"
    CREDIT_APPROVED = "credit_approved"
    CREDIT_REJECTED = "credit_rejected"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class SalesOrder(Base):
    __tablename__ = "sales_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True, nullable=False)

    # Links
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Order details
    status = Column(Enum(SalesOrderStatus), default=SalesOrderStatus.DRAFT, index=True)

    # Financial
    subtotal = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)

    # Credit check
    credit_check_status = Column(String, nullable=True)  # approved, rejected, pending
    credit_check_notes = Column(Text, nullable=True)

    # Delivery
    delivery_address = Column(Text, nullable=True)
    requested_delivery_date = Column(Date, nullable=True)
    actual_delivery_date = Column(Date, nullable=True)

    # Terms
    payment_terms = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    # Multi-tenant
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    customer = relationship("Customer", back_populates="sales_orders")
    quote = relationship("Quote", back_populates="sales_orders")
    created_by = relationship("User", foreign_keys=[created_by_id])

    def __repr__(self):
        return f"<SalesOrder {self.order_number} - {self.status}>"
