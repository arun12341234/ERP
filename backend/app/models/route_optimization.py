"""
Route Optimization model - delivery route planning and optimization.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Float, Enum
from app.core.database import Base
from app.core.config import settings
import enum


class RouteOptimizationStatus(str, enum.Enum):
    DRAFT = "draft"
    OPTIMIZED = "optimized"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class RouteOptimization(Base):
    __tablename__ = "route_optimizations"

    id = Column(Integer, primary_key=True, index=True)
    route_number = Column(String, unique=True, index=True, nullable=False)

    # Route details
    route_date = Column(Date, nullable=False)
    route_name = Column(String, nullable=True)

    # Vehicle/Driver
    vehicle_number = Column(String, nullable=True)
    driver_name = Column(String, nullable=True)

    # Origin
    start_location = Column(String, nullable=False)
    start_latitude = Column(Float, nullable=True)
    start_longitude = Column(Float, nullable=True)

    # Metrics
    number_of_stops = Column(Integer, default=0)
    total_distance_km = Column(Float, default=0.0)
    estimated_duration_hours = Column(Float, default=0.0)

    # Optimization results
    route_sequence = Column(Text, nullable=True)  # JSON array of stop IDs
    optimization_score = Column(Float, default=0.0)  # 0-100

    # Cost (in cents)
    estimated_fuel_cost = Column(Integer, default=0)

    # Status
    status = Column(Enum(RouteOptimizationStatus), default=RouteOptimizationStatus.DRAFT)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<RouteOptimization {self.route_number}>"
