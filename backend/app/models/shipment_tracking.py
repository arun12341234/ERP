"""
Shipment Tracking model - real-time GPS tracking updates.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings


class ShipmentTracking(Base):
    __tablename__ = "shipment_trackings"

    id = Column(Integer, primary_key=True, index=True)

    # Shipment reference
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)

    # Tracking update
    update_timestamp = Column(DateTime, nullable=False, index=True)
    status_message = Column(String, nullable=False)
    location = Column(String, nullable=True)

    # GPS coordinates
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Additional details
    remarks = Column(Text, nullable=True)

    # Estimated time
    estimated_arrival = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    shipment = relationship("Shipment")

    def __repr__(self):
        return f"<ShipmentTracking Shipment:{self.shipment_id} at {self.update_timestamp}>"
