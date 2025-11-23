"""
Machine Schedule model - machine scheduling for work orders.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class ScheduleStatus(str, enum.Enum):
    PLANNED = "planned"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MachineSchedule(Base):
    __tablename__ = "machine_schedules"

    id = Column(Integer, primary_key=True, index=True)

    # Machine
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)

    # Work order
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)

    # Schedule
    scheduled_start = Column(DateTime, nullable=False)
    scheduled_end = Column(DateTime, nullable=False)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)

    # Hours
    planned_hours = Column(Float, nullable=False)
    actual_hours = Column(Float, default=0.0)

    # Status
    status = Column(Enum(ScheduleStatus), default=ScheduleStatus.PLANNED)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    machine = relationship("Machine")
    work_order = relationship("WorkOrder")

    def __repr__(self):
        return f"<MachineSchedule Machine:{self.machine_id} WO:{self.work_order_id}>"
