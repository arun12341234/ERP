"""
Tax Filing model - GST/VAT/sales tax filing and compliance.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Enum
from app.core.database import Base
from app.core.config import settings
import enum


class TaxFilingStatus(str, enum.Enum):
    DRAFT = "draft"
    CALCULATED = "calculated"
    FILED = "filed"
    PAID = "paid"


class TaxType(str, enum.Enum):
    GST = "gst"
    VAT = "vat"
    SALES_TAX = "sales_tax"
    USE_TAX = "use_tax"


class TaxFiling(Base):
    __tablename__ = "tax_filings"

    id = Column(Integer, primary_key=True, index=True)
    filing_number = Column(String, unique=True, index=True, nullable=False)

    # Filing details
    tax_type = Column(Enum(TaxType), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    filing_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=False)

    # Tax calculations (in cents)
    output_tax = Column(Integer, default=0)  # Tax collected on sales
    input_tax = Column(Integer, default=0)   # Tax paid on purchases
    net_tax = Column(Integer, default=0)     # Tax payable/(refundable)

    # Additional details
    total_sales = Column(Integer, default=0)
    total_purchases = Column(Integer, default=0)

    # Status
    status = Column(Enum(TaxFilingStatus), default=TaxFilingStatus.DRAFT)

    # Filing
    filed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    confirmation_number = Column(String, nullable=True)

    # Payment
    payment_date = Column(Date, nullable=True)
    payment_reference = Column(String, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<TaxFiling {self.filing_number}>"
