"""
Loading Plan model - loading optimization and planning.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class LoadingPlanStatus(str, enum.Enum):
    DRAFT = "draft"
    OPTIMIZED = "optimized"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class LoadingPlan(Base):
    __tablename__ = "loading_plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_number = Column(String, unique=True, index=True, nullable=False)

    # Logistics request reference
    logistics_request_id = Column(Integer, ForeignKey("logistics_requests.id"), nullable=True)

    # Vehicle details
    vehicle_type = Column(String, nullable=True)
    vehicle_number = Column(String, nullable=True)
    vehicle_capacity_kg = Column(Float, default=0.0)
    vehicle_capacity_cbm = Column(Float, default=0.0)

    # Loading details
    loading_date = Column(Date, nullable=False)
    loading_location = Column(String, nullable=False)

    # Optimization metrics
    total_weight_planned = Column(Float, default=0.0)
    total_volume_planned = Column(Float, default=0.0)
    weight_utilization_percent = Column(Float, default=0.0)
    volume_utilization_percent = Column(Float, default=0.0)

    # Status
    status = Column(Enum(LoadingPlanStatus), default=LoadingPlanStatus.DRAFT)

    # Loading sequence (JSON or text)
    loading_sequence = Column(Text, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<LoadingPlan {self.plan_number}>"
