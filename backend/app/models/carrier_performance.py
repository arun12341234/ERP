"""
Carrier Performance model - carrier performance tracking and rating.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Float
from app.core.database import Base
from app.core.config import settings


class CarrierPerformance(Base):
    __tablename__ = "carrier_performances"

    id = Column(Integer, primary_key=True, index=True)
    review_number = Column(String, unique=True, index=True, nullable=False)

    # Carrier details
    carrier_name = Column(String, nullable=False, index=True)
    carrier_code = Column(String, nullable=True)

    # Review period
    review_date = Column(Date, nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    # Performance metrics
    total_shipments = Column(Integer, default=0)
    on_time_deliveries = Column(Integer, default=0)
    on_time_percentage = Column(Float, default=0.0)

    damaged_shipments = Column(Integer, default=0)
    lost_shipments = Column(Integer, default=0)

    average_delivery_time_days = Column(Float, default=0.0)
    average_cost_per_shipment = Column(Integer, default=0)  # in cents

    # Ratings (1-5 scale)
    timeliness_rating = Column(Float, default=0.0)
    cost_rating = Column(Float, default=0.0)
    reliability_rating = Column(Float, default=0.0)
    communication_rating = Column(Float, default=0.0)
    overall_rating = Column(Float, default=0.0)

    # Recommendation
    is_recommended = Column(Integer, default=1)  # boolean as int
    performance_tier = Column(String, nullable=True)  # e.g., "gold", "silver", "bronze"

    # Notes
    strengths = Column(Text, nullable=True)
    weaknesses = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<CarrierPerformance {self.carrier_name} - {self.review_number}>"
