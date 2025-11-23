"""
Labor Allocation model - worker assignment to work orders.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class AllocationStatus(str, enum.Enum):
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class LaborAllocation(Base):
    __tablename__ = "labor_allocations"

    id = Column(Integer, primary_key=True, index=True)

    # Worker
    worker_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Work order
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)

    # Role/Skill
    role = Column(String, nullable=True)
    skill_level = Column(String, nullable=True)

    # Schedule
    scheduled_start = Column(DateTime, nullable=False)
    scheduled_end = Column(DateTime, nullable=False)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)

    # Hours
    planned_hours = Column(Float, nullable=False)
    actual_hours = Column(Float, default=0.0)

    # Status
    status = Column(Enum(AllocationStatus), default=AllocationStatus.ASSIGNED)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    worker = relationship("User")
    work_order = relationship("WorkOrder")

    def __repr__(self):
        return f"<LaborAllocation Worker:{self.worker_id} WO:{self.work_order_id}>"
