"""
Depreciation model - depreciation calculation and posting.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class DepreciationStatus(str, enum.Enum):
    CALCULATED = "calculated"
    POSTED = "posted"
    REVERSED = "reversed"


class Depreciation(Base):
    __tablename__ = "depreciations"

    id = Column(Integer, primary_key=True, index=True)
    depreciation_number = Column(String, unique=True, index=True, nullable=False)

    # Asset
    asset_id = Column(Integer, ForeignKey("fixed_assets.id"), nullable=False)

    # Period
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    depreciation_date = Column(Date, nullable=False)

    # Amounts (in cents)
    depreciation_amount = Column(Integer, nullable=False)
    accumulated_depreciation = Column(Integer, nullable=False)
    net_book_value = Column(Integer, nullable=False)

    # Status
    status = Column(Enum(DepreciationStatus), default=DepreciationStatus.CALCULATED)

    # Journal entry reference
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=True)

    # Posted by
    posted_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    posted_date = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    asset = relationship("FixedAsset")

    def __repr__(self):
        return f"<Depreciation {self.depreciation_number}>"
