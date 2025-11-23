"""
Vendor Quotation model - vendor price quotes.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Date, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings


class VendorQuotation(Base):
    __tablename__ = "vendor_quotations"

    id = Column(Integer, primary_key=True, index=True)
    quotation_number = Column(String, unique=True, index=True, nullable=False)

    # Vendor
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)

    # Product
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Pricing
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    # Terms
    payment_terms = Column(String, nullable=True)
    delivery_time = Column(String, nullable=True)
    valid_until = Column(Date, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Selection
    is_selected = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    vendor = relationship("Vendor", back_populates="quotations")
    product = relationship("Product")

    def __repr__(self):
        return f"<VendorQuotation {self.quotation_number}>"
