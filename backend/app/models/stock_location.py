"""
Stock Location & Inventory models - warehouse management.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings


class StockLocation(Base):
    __tablename__ = "stock_locations"

    id = Column(Integer, primary_key=True, index=True)
    location_code = Column(String, unique=True, index=True, nullable=False)

    # Location details
    warehouse = Column(String, nullable=False)
    aisle = Column(String, nullable=True)
    rack = Column(String, nullable=True)
    bin = Column(String, nullable=True)

    # Capacity
    capacity = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    stock_items = relationship("StockItem", back_populates="location")

    def __repr__(self):
        return f"<StockLocation {self.location_code}>"


class StockItem(Base):
    __tablename__ = "stock_items"

    id = Column(Integer, primary_key=True, index=True)

    # Product & Location
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("stock_locations.id"), nullable=False)

    # Quantity
    quantity = Column(Float, default=0.0)

    # Valuation
    unit_cost = Column(Float, default=0.0)
    total_value = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    product = relationship("Product")
    location = relationship("StockLocation", back_populates="stock_items")

    def __repr__(self):
        return f"<StockItem Product:{self.product_id} @ {self.location_id}>"
