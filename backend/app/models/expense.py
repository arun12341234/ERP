"""
Expense model - expense recording and tracking.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class ExpenseStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    POSTED = "posted"
    REJECTED = "rejected"


class ExpenseCategory(str, enum.Enum):
    TRAVEL = "travel"
    MEALS = "meals"
    OFFICE_SUPPLIES = "office_supplies"
    UTILITIES = "utilities"
    RENT = "rent"
    SALARIES = "salaries"
    PROFESSIONAL_FEES = "professional_fees"
    MARKETING = "marketing"
    OTHER = "other"


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    expense_number = Column(String, unique=True, index=True, nullable=False)

    # Expense details
    expense_date = Column(Date, nullable=False)
    category = Column(Enum(ExpenseCategory), nullable=False)
    description = Column(Text, nullable=False)

    # Amount (in cents)
    amount = Column(Integer, nullable=False)
    tax_amount = Column(Integer, default=0)
    total_amount = Column(Integer, nullable=False)

    # Vendor/Payee
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    payee_name = Column(String, nullable=True)

    # GL Account
    account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True)

    # Cost center
    cost_center_id = Column(Integer, ForeignKey("cost_centers.id"), nullable=True)

    # Status
    status = Column(Enum(ExpenseStatus), default=ExpenseStatus.DRAFT)

    # Approvals
    submitted_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approval_date = Column(DateTime, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    submitted_by = relationship("User", foreign_keys=[submitted_by_id])

    def __repr__(self):
        return f"<Expense {self.expense_number}>"
