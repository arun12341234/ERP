"""
Loyalty Points model - customer loyalty and rewards program.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class LoyaltyTier(str, enum.Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


class PointsTransactionType(str, enum.Enum):
    EARNED = "earned"
    REDEEMED = "redeemed"
    EXPIRED = "expired"
    ADJUSTED = "adjusted"
    REVERSED = "reversed"


class PointsSource(str, enum.Enum):
    PURCHASE = "purchase"
    SIGNUP_BONUS = "signup_bonus"
    REFERRAL = "referral"
    REVIEW = "review"
    BIRTHDAY_BONUS = "birthday_bonus"
    SOCIAL_SHARE = "social_share"
    PROMOTIONAL = "promotional"
    ADMIN_ADJUSTMENT = "admin_adjustment"


class LoyaltyAccount(Base):
    __tablename__ = "loyalty_accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, unique=True, index=True, nullable=False)

    # Customer
    customer_id = Column(Integer, ForeignKey("customers.id"), unique=True, nullable=False)

    # Points balance
    points_balance = Column(Integer, default=0)
    lifetime_points_earned = Column(Integer, default=0)
    lifetime_points_redeemed = Column(Integer, default=0)

    # Tier
    current_tier = Column(Enum(LoyaltyTier), default=LoyaltyTier.BRONZE)
    tier_since = Column(Date, nullable=True)

    # Status
    is_active = Column(Integer, default=1)  # boolean as int

    # Membership
    enrollment_date = Column(Date, default=date.today)
    last_activity_date = Column(Date, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    customer = relationship("Customer")

    def __repr__(self):
        return f"<LoyaltyAccount {self.account_number}>"


class PointsTransaction(Base):
    __tablename__ = "points_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_number = Column(String, unique=True, index=True, nullable=False)

    # Loyalty account
    loyalty_account_id = Column(Integer, ForeignKey("loyalty_accounts.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    # Transaction details
    transaction_type = Column(Enum(PointsTransactionType), nullable=False)
    points_source = Column(Enum(PointsSource), nullable=True)
    points = Column(Integer, nullable=False)

    # Balance tracking
    balance_before = Column(Integer, default=0)
    balance_after = Column(Integer, default=0)

    # Reference
    reference_type = Column(String, nullable=True)  # online_order, review, etc.
    reference_id = Column(Integer, nullable=True)
    reference_number = Column(String, nullable=True)

    # Expiry (for earned points)
    expires_at = Column(Date, nullable=True)
    is_expired = Column(Integer, default=0)  # boolean as int

    # Multiplier (for promotional campaigns)
    points_multiplier = Column(Integer, default=1)

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
        return f"<PointsTransaction {self.transaction_number}>"
