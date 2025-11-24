"""
Chart of Accounts model - GL account master.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum
from app.core.database import Base
from app.core.config import settings
import enum


class AccountType(str, enum.Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class ChartOfAccounts(Base):
    __tablename__ = "chart_of_accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_code = Column(String, unique=True, index=True, nullable=False)
    account_name = Column(String, nullable=False)

    # Account classification
    account_type = Column(Enum(AccountType), nullable=False)
    account_subtype = Column(String, nullable=True)  # e.g., "Cash", "Trade Receivables"

    # Hierarchy
    parent_account_id = Column(Integer, nullable=True)
    level = Column(Integer, default=1)

    # Attributes
    is_active = Column(Boolean, default=True)
    is_control_account = Column(Boolean, default=False)
    allow_posting = Column(Boolean, default=True)

    # Balance tracking
    opening_balance = Column(Integer, default=0)  # in cents
    current_balance = Column(Integer, default=0)  # in cents

    # Description
    description = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<ChartOfAccounts {self.account_code} - {self.account_name}>"
