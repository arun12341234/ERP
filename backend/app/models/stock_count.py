"""
Stock Count model - physical inventory counting.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
from app.core.config import settings


class StockCountStatus(str, enum.Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    RECONCILED = "reconciled"


class StockCount(Base):
    __tablename__ = "stock_counts"

    id = Column(Integer, primary_key=True, index=True)
    count_number = Column(String, unique=True, index=True, nullable=False)

    # Product & Location
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("stock_locations.id"), nullable=False)

    # Quantities
    system_quantity = Column(Float, nullable=False)  # From system
    physical_quantity = Column(Float, nullable=True)  # Actual count
    variance = Column(Float, nullable=True)  # Difference

    # Status
    status = Column(Enum(StockCountStatus), default=StockCountStatus.PLANNED)

    # Personnel
    counted_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    scheduled_date = Column(DateTime, nullable=True)
    count_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    product = relationship("Product")
    location = relationship("StockLocation")
    counted_by = relationship("User")

    def __repr__(self):
        return f"<StockCount {self.count_number} - {self.status}>"
