"""
Shipment model - shipment dispatch and delivery tracking.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class ShipmentStatus(str, enum.Enum):
    PENDING = "pending"
    PICKED = "picked"
    PACKED = "packed"
    DISPATCHED = "dispatched"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETURNED = "returned"


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    shipment_number = Column(String, unique=True, index=True, nullable=False)
    tracking_number = Column(String, unique=True, index=True, nullable=True)

    # Order reference
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=True)
    logistics_request_id = Column(Integer, ForeignKey("logistics_requests.id"), nullable=True)

    # Customer
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    # Shipment details
    shipment_date = Column(Date, nullable=False)
    expected_delivery_date = Column(Date, nullable=True)
    actual_delivery_date = Column(Date, nullable=True)

    # Carrier
    carrier_name = Column(String, nullable=True)
    carrier_service = Column(String, nullable=True)

    # Package details
    total_weight_kg = Column(Float, default=0.0)
    number_of_packages = Column(Integer, default=1)

    # Addresses
    origin_address = Column(Text, nullable=False)
    destination_address = Column(Text, nullable=False)

    # Status
    status = Column(Enum(ShipmentStatus), default=ShipmentStatus.PENDING)

    # Delivery challan number
    challan_number = Column(String, nullable=True)

    # Costs (in cents)
    shipping_cost = Column(Integer, default=0)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    customer = relationship("Customer")

    def __repr__(self):
        return f"<Shipment {self.shipment_number}>"
