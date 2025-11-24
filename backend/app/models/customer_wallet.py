"""
Customer Wallet model - digital wallet and store credit management.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class WalletTransactionType(str, enum.Enum):
    CREDIT = "credit"
    DEBIT = "debit"


class WalletTransactionSource(str, enum.Enum):
    TOP_UP = "top_up"
    REFUND = "refund"
    CASHBACK = "cashback"
    BONUS = "bonus"
    PURCHASE = "purchase"
    WITHDRAWAL = "withdrawal"
    EXPIRY = "expiry"
    ADMIN_ADJUSTMENT = "admin_adjustment"


class CustomerWallet(Base):
    __tablename__ = "customer_wallets"

    id = Column(Integer, primary_key=True, index=True)
    wallet_number = Column(String, unique=True, index=True, nullable=False)

    # Customer
    customer_id = Column(Integer, ForeignKey("customers.id"), unique=True, nullable=False)

    # Balance (in cents)
    balance = Column(Integer, default=0)
    credit_limit = Column(Integer, default=0)  # optional credit facility

    # Status
    is_active = Column(Integer, default=1)  # boolean as int
    is_locked = Column(Integer, default=0)  # boolean as int

    # Security
    pin_hash = Column(String, nullable=True)  # for wallet PIN
    last_transaction_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    customer = relationship("Customer")

    def __repr__(self):
        return f"<CustomerWallet {self.wallet_number}>"


class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_number = Column(String, unique=True, index=True, nullable=False)

    # Wallet
    wallet_id = Column(Integer, ForeignKey("customer_wallets.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    # Transaction details
    transaction_type = Column(Enum(WalletTransactionType), nullable=False)
    transaction_source = Column(Enum(WalletTransactionSource), nullable=False)
    amount = Column(Integer, nullable=False)  # in cents

    # Balance tracking
    balance_before = Column(Integer, default=0)
    balance_after = Column(Integer, default=0)

    # Reference
    reference_type = Column(String, nullable=True)  # online_order, return_request, etc.
    reference_id = Column(Integer, nullable=True)
    reference_number = Column(String, nullable=True)

    # Payment details (for top-ups)
    payment_method = Column(String, nullable=True)
    payment_transaction_id = Column(String, nullable=True)
    payment_status = Column(String, default="completed")

    # Description
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Metadata
    processed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Timestamps
    transaction_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    customer = relationship("Customer")

    def __repr__(self):
        return f"<WalletTransaction {self.transaction_number}>"
