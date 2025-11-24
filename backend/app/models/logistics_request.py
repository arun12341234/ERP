"""
Logistics Request model - shipping request management.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class LogisticsRequestStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    TRANSPORTER_ASSIGNED = "transporter_assigned"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class TransportMode(str, enum.Enum):
    ROAD = "road"
    RAIL = "rail"
    AIR = "air"
    SEA = "sea"
    MULTIMODAL = "multimodal"


class LogisticsRequest(Base):
    __tablename__ = "logistics_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_number = Column(String, unique=True, index=True, nullable=False)

    # Order reference
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=True)

    # Shipment details
    pickup_date = Column(Date, nullable=False)
    delivery_date = Column(Date, nullable=False)
    transport_mode = Column(Enum(TransportMode), nullable=False)

    # Origin/Destination
    origin_location = Column(String, nullable=False)
    destination_location = Column(String, nullable=False)
    distance_km = Column(Float, default=0.0)

    # Cargo details
    total_weight_kg = Column(Float, nullable=False)
    total_volume_cbm = Column(Float, default=0.0)
    number_of_packages = Column(Integer, default=1)

    # Transporter
    transporter_name = Column(String, nullable=True)
    transporter_id = Column(Integer, nullable=True)

    # Costs (in cents)
    estimated_cost = Column(Integer, default=0)
    actual_cost = Column(Integer, default=0)

    # Status
    status = Column(Enum(LogisticsRequestStatus), default=LogisticsRequestStatus.DRAFT)

    # Special requirements
    special_instructions = Column(Text, nullable=True)
    requires_temperature_control = Column(Integer, default=0)  # boolean as int

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<LogisticsRequest {self.request_number}>"
