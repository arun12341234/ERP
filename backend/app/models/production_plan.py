"""
Production Plan model - capacity planning and production scheduling.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Float, Enum
from app.core.database import Base
from app.core.config import settings
import enum


class PlanStatus(str, enum.Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProductionPlan(Base):
    __tablename__ = "production_plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_number = Column(String, unique=True, index=True, nullable=False)

    # Planning period
    plan_date = Column(Date, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    # Capacity planning
    total_capacity_hours = Column(Float, default=0.0)
    allocated_hours = Column(Float, default=0.0)
    utilization_percent = Column(Float, default=0.0)

    # Status
    status = Column(Enum(PlanStatus), default=PlanStatus.DRAFT)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<ProductionPlan {self.plan_number}>"
