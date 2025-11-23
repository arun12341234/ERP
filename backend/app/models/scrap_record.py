"""
Scrap Record model - scrap/waste recording.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class ScrapReason(str, enum.Enum):
    PRODUCTION_DEFECT = "production_defect"
    MACHINE_ERROR = "machine_error"
    MATERIAL_DEFECT = "material_defect"
    OPERATOR_ERROR = "operator_error"
    QUALITY_FAILURE = "quality_failure"
    DAMAGE = "damage"
    EXPIRED = "expired"
    OTHER = "other"


class ScrapRecord(Base):
    __tablename__ = "scrap_records"

    id = Column(Integer, primary_key=True, index=True)
    scrap_number = Column(String, unique=True, index=True, nullable=False)

    # Work order (optional)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=True)

    # Product
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Scrap details
    quantity_scrapped = Column(Float, nullable=False)
    scrap_reason = Column(Enum(ScrapReason), nullable=False)
    description = Column(Text, nullable=True)

    # Cost
    unit_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)

    # Recorded by
    recorded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    scrap_date = Column(DateTime, nullable=False)

    # Disposal
    disposal_method = Column(String, nullable=True)
    disposal_date = Column(DateTime, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    work_order = relationship("WorkOrder")
    product = relationship("Product")

    def __repr__(self):
        return f"<ScrapRecord {self.scrap_number}>"
