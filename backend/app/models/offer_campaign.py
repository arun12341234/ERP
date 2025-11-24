"""
Offer Campaign model - promotional campaigns and discount management.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Float, ForeignKey, Enum
from app.core.database import Base
from app.core.config import settings
import enum


class CampaignType(str, enum.Enum):
    PERCENTAGE_DISCOUNT = "percentage_discount"
    FIXED_AMOUNT_DISCOUNT = "fixed_amount_discount"
    BUY_X_GET_Y = "buy_x_get_y"
    FREE_SHIPPING = "free_shipping"
    CASHBACK = "cashback"
    LOYALTY_MULTIPLIER = "loyalty_multiplier"


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class DiscountAppliesTo(str, enum.Enum):
    ALL_PRODUCTS = "all_products"
    SPECIFIC_PRODUCTS = "specific_products"
    SPECIFIC_CATEGORIES = "specific_categories"
    MINIMUM_PURCHASE = "minimum_purchase"


class OfferCampaign(Base):
    __tablename__ = "offer_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    campaign_code = Column(String, unique=True, index=True, nullable=False)

    # Campaign details
    campaign_name = Column(String, nullable=False)
    campaign_type = Column(Enum(CampaignType), nullable=False)
    description = Column(Text, nullable=True)

    # Status
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)

    # Schedule
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    # Discount rules
    discount_percentage = Column(Float, nullable=True)  # for percentage discount
    discount_amount = Column(Integer, nullable=True)  # in cents, for fixed amount
    minimum_purchase_amount = Column(Integer, default=0)  # in cents
    maximum_discount_amount = Column(Integer, nullable=True)  # cap for percentage discounts

    # Buy X Get Y rules
    buy_quantity = Column(Integer, nullable=True)
    get_quantity = Column(Integer, nullable=True)
    get_discount_percentage = Column(Float, nullable=True)

    # Cashback/Loyalty rules
    cashback_percentage = Column(Float, nullable=True)
    cashback_amount = Column(Integer, nullable=True)  # in cents
    loyalty_points_multiplier = Column(Integer, default=1)

    # Applicability
    applies_to = Column(Enum(DiscountAppliesTo), default=DiscountAppliesTo.ALL_PRODUCTS)
    product_ids = Column(Text, nullable=True)  # JSON array
    category_names = Column(Text, nullable=True)  # JSON array
    excluded_product_ids = Column(Text, nullable=True)  # JSON array

    # Usage limits
    usage_limit_total = Column(Integer, nullable=True)  # null = unlimited
    usage_limit_per_customer = Column(Integer, default=1)
    usage_count = Column(Integer, default=0)

    # Customer eligibility
    customer_segment = Column(String, nullable=True)  # all, new, returning, vip
    minimum_loyalty_tier = Column(String, nullable=True)

    # Coupon settings
    is_coupon_required = Column(Integer, default=1)  # boolean as int
    coupon_code = Column(String, unique=True, index=True, nullable=True)
    auto_apply = Column(Integer, default=0)  # boolean as int

    # Marketing
    banner_image = Column(String, nullable=True)
    terms_and_conditions = Column(Text, nullable=True)

    # Publishing
    is_published = Column(Integer, default=0)  # boolean as int
    published_at = Column(DateTime, nullable=True)
    published_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Analytics
    conversion_count = Column(Integer, default=0)
    total_discount_given = Column(Integer, default=0)  # in cents
    total_revenue = Column(Integer, default=0)  # in cents

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<OfferCampaign {self.campaign_code} - {self.campaign_name}>"


class CouponUsage(Base):
    __tablename__ = "coupon_usages"

    id = Column(Integer, primary_key=True, index=True)

    # Campaign
    campaign_id = Column(Integer, ForeignKey("offer_campaigns.id"), nullable=False)
    coupon_code = Column(String, nullable=False, index=True)

    # Customer
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    # Order
    online_order_id = Column(Integer, ForeignKey("online_orders.id"), nullable=False)
    order_number = Column(String, nullable=False)

    # Discount applied
    discount_amount = Column(Integer, nullable=False)  # in cents
    order_total = Column(Integer, nullable=False)  # in cents

    # Timestamps
    used_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<CouponUsage {self.coupon_code}>"
