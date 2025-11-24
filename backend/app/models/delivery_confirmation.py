"""
Delivery Confirmation model - proof of delivery (POD).
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings


class DeliveryConfirmation(Base):
    __tablename__ = "delivery_confirmations"

    id = Column(Integer, primary_key=True, index=True)
    confirmation_number = Column(String, unique=True, index=True, nullable=False)

    # Shipment reference
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=False)

    # Delivery details
    delivery_timestamp = Column(DateTime, nullable=False)
    received_by_name = Column(String, nullable=False)
    received_by_signature = Column(String, nullable=True)  # Path to signature image

    # Proof of delivery
    pod_image = Column(String, nullable=True)  # Path to POD image/scan
    pod_notes = Column(Text, nullable=True)

    # Condition
    delivery_condition = Column(String, nullable=True)  # e.g., "good", "damaged"
    exceptions = Column(Text, nullable=True)

    # Confirmed by
    confirmed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    shipment = relationship("Shipment")

    def __repr__(self):
        return f"<DeliveryConfirmation {self.confirmation_number}>"
