"""
Product/Item Master model - central product catalog.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, Enum
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
from app.core.config import settings


class ProductType(str, enum.Enum):
    RAW_MATERIAL = "raw_material"
    FINISHED_GOOD = "finished_good"
    SEMI_FINISHED = "semi_finished"
    SERVICE = "service"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)

    # Basic info
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    product_type = Column(Enum(ProductType), default=ProductType.FINISHED_GOOD)

    # Categorization
    category = Column(String, nullable=True)
    brand = Column(String, nullable=True)

    # Units
    unit_of_measure = Column(String, default="pcs")  # pcs, kg, liter, etc.

    # Pricing
    cost_price = Column(Float, default=0.0)
    selling_price = Column(Float, default=0.0)

    # Inventory
    reorder_level = Column(Integer, default=0)
    reorder_quantity = Column(Integer, default=0)

    # Flags
    is_active = Column(Boolean, default=True)
    track_inventory = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    bom_items = relationship("BOMItem", back_populates="product", foreign_keys="BOMItem.product_id")

    def __repr__(self):
        return f"<Product {self.sku} - {self.name}>"
