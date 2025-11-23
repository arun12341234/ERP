"""
Downtime model - machine downtime tracking.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class DowntimeType(str, enum.Enum):
    BREAKDOWN = "breakdown"
    PLANNED_MAINTENANCE = "planned_maintenance"
    SETUP_CHANGEOVER = "setup_changeover"
    NO_MATERIAL = "no_material"
    NO_OPERATOR = "no_operator"
    QUALITY_ISSUE = "quality_issue"
    OTHER = "other"


class Downtime(Base):
    __tablename__ = "downtimes"

    id = Column(Integer, primary_key=True, index=True)

    # Machine
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)

    # Work order (optional)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=True)

    # Downtime details
    downtime_type = Column(Enum(DowntimeType), nullable=False)
    reason = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    # Time tracking
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_hours = Column(Float, default=0.0)

    # Reported by
    reported_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Resolution
    resolution = Column(Text, nullable=True)
    resolved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    machine = relationship("Machine")
    work_order = relationship("WorkOrder")

    def __repr__(self):
        return f"<Downtime Machine:{self.machine_id} Type:{self.downtime_type}>"
