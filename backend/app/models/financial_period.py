"""
Financial Period model - accounting period management and closing.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Enum, Boolean
from app.core.database import Base
from app.core.config import settings
import enum


class PeriodStatus(str, enum.Enum):
    OPEN = "open"
    CLOSING = "closing"
    CLOSED = "closed"
    LOCKED = "locked"


class FinancialPeriod(Base):
    __tablename__ = "financial_periods"

    id = Column(Integer, primary_key=True, index=True)
    period_number = Column(String, unique=True, index=True, nullable=False)

    # Period details
    period_name = Column(String, nullable=False)  # e.g., "Q1 2024", "January 2024"
    fiscal_year = Column(Integer, nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    # Status
    status = Column(Enum(PeriodStatus), default=PeriodStatus.OPEN)
    is_year_end = Column(Boolean, default=False)

    # Closing
    closed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    closed_date = Column(DateTime, nullable=True)

    # Trial balance (in cents)
    total_debits = Column(Integer, default=0)
    total_credits = Column(Integer, default=0)
    is_balanced = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<FinancialPeriod {self.period_number} - {self.period_name}>"
