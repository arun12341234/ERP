"""
Warehouse Slot model - warehouse slotting and bin assignment.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class SlotType(str, enum.Enum):
    FAST_MOVING = "fast_moving"
    MEDIUM_MOVING = "medium_moving"
    SLOW_MOVING = "slow_moving"
    BULK_STORAGE = "bulk_storage"
    HAZARDOUS = "hazardous"
    TEMPERATURE_CONTROLLED = "temperature_controlled"


class WarehouseSlot(Base):
    __tablename__ = "warehouse_slots"

    id = Column(Integer, primary_key=True, index=True)

    # Product
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Stock location (bin)
    location_id = Column(Integer, ForeignKey("stock_locations.id"), nullable=False)

    # Slot details
    slot_type = Column(Enum(SlotType), nullable=False)
    slot_priority = Column(Integer, default=5)  # 1-10, higher is more accessible

    # Product characteristics
    velocity_category = Column(String, nullable=True)  # ABC analysis
    pick_frequency_per_day = Column(Float, default=0.0)

    # Optimization metrics
    distance_from_dispatch_m = Column(Float, default=0.0)
    optimal_slot_score = Column(Float, default=0.0)  # 0-100

    # Assignment
    assigned_date = Column(DateTime, nullable=True)
    is_active = Column(Integer, default=1)  # boolean as int

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    product = relationship("Product")
    location = relationship("StockLocation")

    def __repr__(self):
        return f"<WarehouseSlot Product:{self.product_id} Location:{self.location_id}>"
