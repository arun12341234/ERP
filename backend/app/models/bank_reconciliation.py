"""
Bank Reconciliation model - bank statement matching.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class ReconciliationStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"


class BankReconciliation(Base):
    __tablename__ = "bank_reconciliations"

    id = Column(Integer, primary_key=True, index=True)
    reconciliation_number = Column(String, unique=True, index=True, nullable=False)

    # Bank account
    bank_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=False)

    # Period
    statement_date = Column(Date, nullable=False)
    reconciliation_date = Column(Date, nullable=False)

    # Balances (in cents)
    opening_balance = Column(Integer, default=0)
    closing_balance = Column(Integer, default=0)
    statement_balance = Column(Integer, nullable=False)
    book_balance = Column(Integer, nullable=False)
    difference = Column(Integer, default=0)

    # Status
    status = Column(Enum(ReconciliationStatus), default=ReconciliationStatus.IN_PROGRESS)

    # Reconciled by
    reconciled_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_date = Column(DateTime, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<BankReconciliation {self.reconciliation_number}>"


class BankReconciliationLine(Base):
    """Bank reconciliation line items - matched/unmatched transactions."""
    __tablename__ = "bank_reconciliation_lines"

    id = Column(Integer, primary_key=True, index=True)

    # Reconciliation reference
    reconciliation_id = Column(Integer, ForeignKey("bank_reconciliations.id"), nullable=False)

    # Transaction details
    transaction_date = Column(Date, nullable=False)
    description = Column(String, nullable=False)
    reference = Column(String, nullable=True)

    # Amount (in cents)
    amount = Column(Integer, nullable=False)

    # Matching
    is_matched = Column(Boolean, default=False)
    matched_transaction_id = Column(Integer, nullable=True)  # Reference to payment/receipt

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    reconciliation = relationship("BankReconciliation")

    def __repr__(self):
        return f"<BankReconciliationLine Recon:{self.reconciliation_id}>"
