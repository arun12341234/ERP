"""
Rework Order model - rework orders for failed quality checks.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class ReworkStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SCRAPPED = "scrapped"
    CANCELLED = "cancelled"


class ReworkOrder(Base):
    __tablename__ = "rework_orders"

    id = Column(Integer, primary_key=True, index=True)
    rework_number = Column(String, unique=True, index=True, nullable=False)

    # Original work order
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)

    # Quality check that triggered rework
    quality_check_id = Column(Integer, ForeignKey("quality_checks_production.id"), nullable=True)

    # Product
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Quantities
    quantity_to_rework = Column(Float, nullable=False)
    quantity_completed = Column(Float, default=0.0)
    quantity_scrapped = Column(Float, default=0.0)

    # Defect details
    defect_description = Column(Text, nullable=False)
    rework_instructions = Column(Text, nullable=True)

    # Status
    status = Column(Enum(ReworkStatus), default=ReworkStatus.PENDING)

    # Cost
    estimated_cost = Column(Float, default=0.0)
    actual_cost = Column(Float, default=0.0)

    # Assigned to
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)

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
        return f"<ReworkOrder {self.rework_number}>"
