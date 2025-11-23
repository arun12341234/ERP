"""
Preventive Maintenance model - scheduled preventive maintenance.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class PMStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class PreventiveMaintenance(Base):
    __tablename__ = "preventive_maintenances"

    id = Column(Integer, primary_key=True, index=True)
    pm_number = Column(String, unique=True, index=True, nullable=False)

    # Machine
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)

    # PM Plan details
    pm_type = Column(String, nullable=False)  # e.g., "Daily check", "Monthly service"
    description = Column(Text, nullable=True)
    checklist = Column(Text, nullable=True)  # JSON or text checklist

    # Schedule
    scheduled_date = Column(DateTime, nullable=False)
    frequency_days = Column(Integer, nullable=True)  # For recurring PM

    # Execution
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    duration_hours = Column(Float, default=0.0)

    # Status
    status = Column(Enum(PMStatus), default=PMStatus.SCHEDULED)

    # Assigned to
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Results
    work_performed = Column(Text, nullable=True)
    parts_replaced = Column(Text, nullable=True)
    findings = Column(Text, nullable=True)

    # Next PM
    next_pm_date = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    machine = relationship("Machine")
    assigned_to = relationship("User")

    def __repr__(self):
        return f"<PreventiveMaintenance {self.pm_number}>"
