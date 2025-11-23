"""
Vendor/Supplier model - supplier management.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, Enum
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
from app.core.config import settings


class VendorStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLACKLISTED = "blacklisted"


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    vendor_code = Column(String, unique=True, index=True, nullable=False)

    # Basic info
    name = Column(String, nullable=False, index=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)

    # Address
    address = Column(Text, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)

    # Tax info
    tax_id = Column(String, nullable=True)

    # Payment
    payment_terms = Column(String, nullable=True)  # Net 30, Net 60
    credit_limit = Column(Float, default=0.0)

    # Rating
    rating = Column(Float, default=0.0)  # 0-5 stars

    # Status
    status = Column(Enum(VendorStatus), default=VendorStatus.ACTIVE)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    purchase_orders = relationship("PurchaseOrder", back_populates="vendor")
    quotations = relationship("VendorQuotation", back_populates="vendor")

    def __repr__(self):
        return f"<Vendor {self.vendor_code} - {self.name}>"
