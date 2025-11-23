"""
Customer model - extends beyond basic user for CRM purposes.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, Enum
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
from app.core.config import settings


class CustomerType(str, enum.Enum):
    INDIVIDUAL = "individual"
    BUSINESS = "business"


class CustomerStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    # Link to user account (optional)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Basic info
    name = Column(String, nullable=False, index=True)
    email = Column(String, index=True, nullable=False)
    phone = Column(String, nullable=True)

    # Business info
    customer_type = Column(Enum(CustomerType), default=CustomerType.INDIVIDUAL)
    company_name = Column(String, nullable=True)
    tax_id = Column(String, nullable=True)

    # Address
    billing_address = Column(Text, nullable=True)
    shipping_address = Column(Text, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)

    # Financial
    credit_limit = Column(Float, default=0.0)
    current_balance = Column(Float, default=0.0)
    payment_terms = Column(String, nullable=True)  # e.g., "Net 30"

    # Status
    status = Column(Enum(CustomerStatus), default=CustomerStatus.ACTIVE)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    opportunities = relationship("Opportunity", back_populates="customer")
    quotes = relationship("Quote", back_populates="customer")
    sales_orders = relationship("SalesOrder", back_populates="customer")
    feedback = relationship("Feedback", back_populates="customer")
    tickets = relationship("SupportTicket", back_populates="customer")
    contracts = relationship("Contract", back_populates="customer")

    def __repr__(self):
        return f"<Customer {self.name} - {self.status}>"
