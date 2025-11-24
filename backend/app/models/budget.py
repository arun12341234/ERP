"""
Budget model - departmental and organizational budgeting.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Enum
from app.core.database import Base
from app.core.config import settings
import enum


class BudgetStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ACTIVE = "active"
    CLOSED = "closed"


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    budget_number = Column(String, unique=True, index=True, nullable=False)

    # Budget details
    budget_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Period
    fiscal_year = Column(Integer, nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    # Department/Cost center
    department = Column(String, nullable=True)
    cost_center_id = Column(Integer, ForeignKey("cost_centers.id"), nullable=True)

    # Amounts (in cents)
    total_budget_amount = Column(Integer, nullable=False)
    allocated_amount = Column(Integer, default=0)
    spent_amount = Column(Integer, default=0)
    remaining_amount = Column(Integer, default=0)

    # Status
    status = Column(Enum(BudgetStatus), default=BudgetStatus.DRAFT)

    # Approvals
    submitted_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approval_date = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<Budget {self.budget_number} - {self.budget_name}>"


class BudgetLine(Base):
    """Budget line items - account-level budget allocations."""
    __tablename__ = "budget_lines"

    id = Column(Integer, primary_key=True, index=True)

    # Budget reference
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=False)

    # GL Account
    account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=False)

    # Amounts (in cents)
    budgeted_amount = Column(Integer, nullable=False)
    spent_amount = Column(Integer, default=0)
    remaining_amount = Column(Integer, default=0)

    # Description
    description = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<BudgetLine Budget:{self.budget_id} Account:{self.account_id}>"
