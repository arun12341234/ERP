"""
Work Order model - manufacturing work orders.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class WorkOrderStatus(str, enum.Enum):
    DRAFT = "draft"
    RELEASED = "released"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True)
    wo_number = Column(String, unique=True, index=True, nullable=False)

    # Product
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Production plan reference
    production_plan_id = Column(Integer, ForeignKey("production_plans.id"), nullable=True)

    # Quantities
    quantity_planned = Column(Float, nullable=False)
    quantity_produced = Column(Float, default=0.0)
    quantity_scrapped = Column(Float, default=0.0)

    # Schedule
    scheduled_start = Column(DateTime, nullable=True)
    scheduled_end = Column(DateTime, nullable=True)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)

    # Priority
    priority = Column(Integer, default=5)  # 1-10, higher is more urgent

    # Status
    status = Column(Enum(WorkOrderStatus), default=WorkOrderStatus.DRAFT)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    product = relationship("Product")

    def __repr__(self):
        return f"<WorkOrder {self.wo_number}>"
