"""
Cold Chain Monitoring model - temperature monitoring for cold chain logistics.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class TemperatureStatus(str, enum.Enum):
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    BREACH = "breach"


class ColdChainMonitoring(Base):
    __tablename__ = "cold_chain_monitorings"

    id = Column(Integer, primary_key=True, index=True)

    # Shipment reference
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)

    # Sensor details
    sensor_id = Column(String, nullable=False, index=True)
    sensor_location = Column(String, nullable=True)  # e.g., "container_front", "center"

    # Temperature reading
    reading_timestamp = Column(DateTime, nullable=False, index=True)
    temperature_celsius = Column(Float, nullable=False)
    humidity_percent = Column(Float, nullable=True)

    # Thresholds
    min_temperature_celsius = Column(Float, nullable=False)
    max_temperature_celsius = Column(Float, nullable=False)

    # Status
    status = Column(Enum(TemperatureStatus), default=TemperatureStatus.NORMAL)

    # Alert
    is_alert = Column(Integer, default=0)  # boolean as int
    alert_sent = Column(Integer, default=0)  # boolean as int
    alert_message = Column(String, nullable=True)

    # GPS location (optional)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    shipment = relationship("Shipment")

    def __repr__(self):
        return f"<ColdChainMonitoring Shipment:{self.shipment_id} Sensor:{self.sensor_id}>"
