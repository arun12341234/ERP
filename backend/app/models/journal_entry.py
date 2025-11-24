"""
Journal Entry model - manual GL entries.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class JournalEntryStatus(str, enum.Enum):
    DRAFT = "draft"
    POSTED = "posted"
    REVERSED = "reversed"


class JournalEntryType(str, enum.Enum):
    STANDARD = "standard"
    ADJUSTING = "adjusting"
    CLOSING = "closing"
    REVERSING = "reversing"


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    entry_number = Column(String, unique=True, index=True, nullable=False)

    # Entry details
    entry_date = Column(Date, nullable=False)
    entry_type = Column(Enum(JournalEntryType), default=JournalEntryType.STANDARD)
    description = Column(Text, nullable=False)

    # Status
    status = Column(Enum(JournalEntryStatus), default=JournalEntryStatus.DRAFT)

    # Posting
    posted_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    posted_date = Column(DateTime, nullable=True)

    # Reversal
    is_reversed = Column(Boolean, default=False)
    reversed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reversed_date = Column(DateTime, nullable=True)
    reversal_entry_id = Column(Integer, nullable=True)

    # Reference
    reference = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<JournalEntry {self.entry_number}>"


class JournalEntryLine(Base):
    """Journal entry line items - debit/credit entries."""
    __tablename__ = "journal_entry_lines"

    id = Column(Integer, primary_key=True, index=True)

    # Journal entry reference
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=False)

    # GL Account
    account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=False)

    # Debit/Credit amounts (in cents)
    debit_amount = Column(Integer, default=0)
    credit_amount = Column(Integer, default=0)

    # Description
    description = Column(Text, nullable=True)

    # Cost center (optional)
    cost_center_id = Column(Integer, ForeignKey("cost_centers.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    journal_entry = relationship("JournalEntry")

    def __repr__(self):
        return f"<JournalEntryLine JE:{self.journal_entry_id} Account:{self.account_id}>"
