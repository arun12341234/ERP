"""
Maintenance Request model - maintenance requests for machines.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class MaintenanceRequestStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MaintenancePriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_number = Column(String, unique=True, index=True, nullable=False)

    # Machine
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)

    # Request details
    issue_description = Column(Text, nullable=False)
    priority = Column(Enum(MaintenancePriority), default=MaintenancePriority.MEDIUM)

    # Status
    status = Column(Enum(MaintenanceRequestStatus), default=MaintenanceRequestStatus.SUBMITTED)

    # Requested by
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    request_date = Column(DateTime, default=datetime.utcnow)

    # Assigned to
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Schedule
    scheduled_date = Column(DateTime, nullable=True)
    completed_date = Column(DateTime, nullable=True)

    # Resolution
    work_performed = Column(Text, nullable=True)
    resolution_notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    machine = relationship("Machine")
    requested_by = relationship("User", foreign_keys=[requested_by_id])

    def __repr__(self):
        return f"<MaintenanceRequest {self.request_number}>"
