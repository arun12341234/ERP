"""
Shopfloor Job model - shopfloor job assignments.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class JobStatus(str, enum.Enum):
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ShopfloorJob(Base):
    __tablename__ = "shopfloor_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_number = Column(String, unique=True, index=True, nullable=False)

    # Work order
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)

    # Worker
    worker_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Machine (optional)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=True)

    # Operation details
    operation_name = Column(String, nullable=False)
    operation_sequence = Column(Integer, default=1)

    # Quantities
    quantity_assigned = Column(Float, nullable=False)
    quantity_completed = Column(Float, default=0.0)

    # Time tracking
    assigned_at = Column(DateTime, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Status
    status = Column(Enum(JobStatus), default=JobStatus.ASSIGNED)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    work_order = relationship("WorkOrder")
    worker = relationship("User")
    machine = relationship("Machine")

    def __repr__(self):
        return f"<ShopfloorJob {self.job_number}>"
