"""
Machine model - production machines and equipment.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, Enum
from app.core.database import Base
from app.core.config import settings
import enum


class MachineStatus(str, enum.Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    BREAKDOWN = "breakdown"
    RETIRED = "retired"


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    machine_code = Column(String, unique=True, index=True, nullable=False)

    # Machine details
    name = Column(String, nullable=False)
    machine_type = Column(String, nullable=True)
    manufacturer = Column(String, nullable=True)
    model = Column(String, nullable=True)

    # Capacity
    hourly_capacity = Column(Float, default=0.0)
    daily_capacity_hours = Column(Float, default=8.0)

    # Status
    status = Column(Enum(MachineStatus), default=MachineStatus.AVAILABLE)
    is_active = Column(Boolean, default=True)

    # Location
    department = Column(String, nullable=True)
    location = Column(String, nullable=True)

    # Maintenance
    last_maintenance_date = Column(DateTime, nullable=True)
    next_maintenance_date = Column(DateTime, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<Machine {self.machine_code}>"
