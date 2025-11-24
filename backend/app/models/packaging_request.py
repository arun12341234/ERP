"""
Packaging Request model - packaging request and fulfillment.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class PackagingRequestStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PACKED = "packed"
    READY_TO_SHIP = "ready_to_ship"
    CANCELLED = "cancelled"


class PackagingRequest(Base):
    __tablename__ = "packaging_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_number = Column(String, unique=True, index=True, nullable=False)

    # Order reference
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=True)

    # Product
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Packaging details
    request_date = Column(Date, nullable=False)
    quantity_to_pack = Column(Float, nullable=False)
    quantity_packed = Column(Float, default=0.0)

    # Packaging specifications
    packaging_type = Column(String, nullable=True)  # e.g., "box", "pallet", "crate"
    packaging_material = Column(String, nullable=True)
    special_handling = Column(Text, nullable=True)

    # Dimensions
    length_cm = Column(Float, nullable=True)
    width_cm = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)

    # Status
    status = Column(Enum(PackagingRequestStatus), default=PackagingRequestStatus.PENDING)

    # Packed by
    packed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    packed_date = Column(DateTime, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    product = relationship("Product")

    def __repr__(self):
        return f"<PackagingRequest {self.request_number}>"
