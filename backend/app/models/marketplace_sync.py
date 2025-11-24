"""
Marketplace Sync model - multi-channel marketplace integration.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class MarketplacePlatform(str, enum.Enum):
    AMAZON = "amazon"
    FLIPKART = "flipkart"
    MEESHO = "meesho"
    SHOPIFY = "shopify"
    ETSY = "etsy"
    EBAY = "ebay"
    WALMART = "walmart"
    MYNTRA = "myntra"


class SyncStatus(str, enum.Enum):
    PENDING = "pending"
    SYNCING = "syncing"
    SYNCED = "synced"
    FAILED = "failed"
    PAUSED = "paused"


class ListingStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"
    DELISTED = "delisted"


class MarketplaceIntegration(Base):
    __tablename__ = "marketplace_integrations"

    id = Column(Integer, primary_key=True, index=True)
    integration_code = Column(String, unique=True, index=True, nullable=False)

    # Platform
    platform = Column(Enum(MarketplacePlatform), nullable=False)
    platform_store_name = Column(String, nullable=True)

    # Credentials
    api_key = Column(String, nullable=True)  # Encrypted
    api_secret = Column(String, nullable=True)  # Encrypted
    seller_id = Column(String, nullable=True)
    access_token = Column(String, nullable=True)  # Encrypted

    # Status
    is_active = Column(Integer, default=1)  # boolean as int
    sync_status = Column(Enum(SyncStatus), default=SyncStatus.PENDING)

    # Sync settings
    auto_sync_enabled = Column(Integer, default=1)  # boolean as int
    sync_frequency_minutes = Column(Integer, default=60)
    last_sync_timestamp = Column(DateTime, nullable=True)
    last_sync_message = Column(Text, nullable=True)

    # Inventory sync
    sync_inventory = Column(Integer, default=1)  # boolean as int
    sync_prices = Column(Integer, default=1)  # boolean as int
    sync_orders = Column(Integer, default=1)  # boolean as int

    # Pricing rules
    price_markup_percentage = Column(Float, default=0.0)
    price_markup_amount = Column(Integer, default=0)  # in cents

    # Commission settings
    commission_percentage = Column(Float, default=0.0)
    fixed_fee_per_order = Column(Integer, default=0)  # in cents

    # Contact
    contact_person = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<MarketplaceIntegration {self.platform} - {self.integration_code}>"


class MarketplaceListing(Base):
    __tablename__ = "marketplace_listings"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(String, unique=True, index=True, nullable=False)

    # Integration
    integration_id = Column(Integer, ForeignKey("marketplace_integrations.id"), nullable=False)
    platform = Column(Enum(MarketplacePlatform), nullable=False)

    # Product
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    website_product_id = Column(Integer, ForeignKey("website_products.id"), nullable=True)

    # Marketplace identifiers
    marketplace_product_id = Column(String, nullable=True, index=True)
    marketplace_sku = Column(String, nullable=True, index=True)

    # Listing details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True)

    # Pricing
    price = Column(Integer, default=0)  # in cents
    compare_at_price = Column(Integer, nullable=True)  # in cents
    cost = Column(Integer, nullable=True)  # in cents

    # Inventory
    quantity = Column(Float, default=0.0)
    low_stock_threshold = Column(Float, default=10.0)

    # Status
    listing_status = Column(Enum(ListingStatus), default=ListingStatus.DRAFT)
    sync_status = Column(Enum(SyncStatus), default=SyncStatus.PENDING)

    # Sync tracking
    last_synced_at = Column(DateTime, nullable=True)
    sync_error_message = Column(Text, nullable=True)

    # Images
    images = Column(Text, nullable=True)  # JSON array

    # Attributes (platform-specific)
    attributes = Column(Text, nullable=True)  # JSON object

    # Analytics
    view_count = Column(Integer, default=0)
    order_count = Column(Integer, default=0)
    total_revenue = Column(Integer, default=0)  # in cents

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    product = relationship("Product")

    def __repr__(self):
        return f"<MarketplaceListing {self.platform} - {self.listing_id}>"
