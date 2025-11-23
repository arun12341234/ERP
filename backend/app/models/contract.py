"""
Contract model - customer contracts with renewal tracking.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float, Date, Boolean
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
from app.core.config import settings


class ContractStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PENDING_RENEWAL = "pending_renewal"
    RENEWED = "renewed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ContractType(str, enum.Enum):
    SERVICE = "service"
    SUBSCRIPTION = "subscription"
    LICENSE = "license"
    MAINTENANCE = "maintenance"
    OTHER = "other"


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    contract_number = Column(String, unique=True, index=True, nullable=False)

    # Links
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Contract details
    contract_type = Column(Enum(ContractType), default=ContractType.SERVICE)
    status = Column(Enum(ContractStatus), default=ContractStatus.DRAFT, index=True)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Financial
    value = Column(Float, default=0.0)
    billing_frequency = Column(String, nullable=True)  # monthly, quarterly, annual

    # Dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    renewal_date = Column(Date, nullable=True)
    auto_renew = Column(Boolean, default=False)

    # Terms
    payment_terms = Column(String, nullable=True)
    terms_and_conditions = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Renewal tracking
    renewal_notified = Column(Boolean, default=False)
    renewal_notified_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activated_at = Column(DateTime, nullable=True)
    renewed_at = Column(DateTime, nullable=True)

    # Multi-tenant
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    customer = relationship("Customer", back_populates="contracts")
    created_by = relationship("User", foreign_keys=[created_by_id])

    def __repr__(self):
        return f"<Contract {self.contract_number} - {self.status}>"

    def is_expiring_soon(self, days=30):
        """Check if contract is expiring within specified days."""
        if not self.end_date:
            return False
        days_until_expiry = (self.end_date - date.today()).days
        return 0 <= days_until_expiry <= days
