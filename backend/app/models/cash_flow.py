"""
Cash Flow model - cash flow statement generation.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Enum
from app.core.database import Base
from app.core.config import settings
import enum


class CashFlowCategory(str, enum.Enum):
    OPERATING = "operating"
    INVESTING = "investing"
    FINANCING = "financing"


class CashFlow(Base):
    __tablename__ = "cash_flows"

    id = Column(Integer, primary_key=True, index=True)
    report_number = Column(String, unique=True, index=True, nullable=False)

    # Period
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    report_date = Column(Date, nullable=False)

    # Opening and closing cash (in cents)
    opening_cash = Column(Integer, default=0)
    closing_cash = Column(Integer, default=0)
    net_change = Column(Integer, default=0)

    # Operating activities (in cents)
    operating_inflows = Column(Integer, default=0)
    operating_outflows = Column(Integer, default=0)
    net_operating = Column(Integer, default=0)

    # Investing activities (in cents)
    investing_inflows = Column(Integer, default=0)
    investing_outflows = Column(Integer, default=0)
    net_investing = Column(Integer, default=0)

    # Financing activities (in cents)
    financing_inflows = Column(Integer, default=0)
    financing_outflows = Column(Integer, default=0)
    net_financing = Column(Integer, default=0)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<CashFlow {self.report_number}>"


class CashFlowLine(Base):
    """Cash flow line items - detailed cash flow entries."""
    __tablename__ = "cash_flow_lines"

    id = Column(Integer, primary_key=True, index=True)

    # Cash flow reference
    cash_flow_id = Column(Integer, nullable=False)

    # Category
    category = Column(Enum(CashFlowCategory), nullable=False)

    # Details
    description = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)  # in cents (positive = inflow, negative = outflow)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<CashFlowLine CashFlow:{self.cash_flow_id}>"
