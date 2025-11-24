"""
Website Product model - online product listing and catalog management.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class ProductVisibility(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    HIDDEN = "hidden"
    OUT_OF_STOCK = "out_of_stock"


class WebsiteProduct(Base):
    __tablename__ = "website_products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)

    # Product reference
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)

    # Product details
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    short_description = Column(Text, nullable=True)
    long_description = Column(Text, nullable=True)

    # Pricing
    price = Column(Integer, default=0)  # in cents
    compare_at_price = Column(Integer, nullable=True)  # in cents
    cost_per_item = Column(Integer, nullable=True)  # in cents

    # Inventory
    stock_quantity = Column(Float, default=0.0)
    low_stock_threshold = Column(Float, default=10.0)
    track_inventory = Column(Integer, default=1)  # boolean as int

    # SEO
    meta_title = Column(String, nullable=True)
    meta_description = Column(Text, nullable=True)
    meta_keywords = Column(Text, nullable=True)

    # Images
    featured_image = Column(String, nullable=True)
    gallery_images = Column(Text, nullable=True)  # JSON array

    # Categorization
    category = Column(String, nullable=True)
    tags = Column(Text, nullable=True)  # JSON array
    brand = Column(String, nullable=True)

    # Visibility
    visibility = Column(Enum(ProductVisibility), default=ProductVisibility.DRAFT)
    is_featured = Column(Integer, default=0)  # boolean as int
    is_new_arrival = Column(Integer, default=0)  # boolean as int
    is_best_seller = Column(Integer, default=0)  # boolean as int

    # Shipping
    weight_kg = Column(Float, nullable=True)
    requires_shipping = Column(Integer, default=1)  # boolean as int

    # Publishing
    published_at = Column(DateTime, nullable=True)
    published_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Analytics
    view_count = Column(Integer, default=0)
    order_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<WebsiteProduct {self.sku} - {self.title}>"
