"""
Stock Transfer model - moving inventory between locations.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
from app.core.config import settings


class TransferStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class StockTransfer(Base):
    __tablename__ = "stock_transfers"

    id = Column(Integer, primary_key=True, index=True)
    transfer_number = Column(String, unique=True, index=True, nullable=False)

    # Product
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)

    # Locations
    from_location_id = Column(Integer, ForeignKey("stock_locations.id"), nullable=False)
    to_location_id = Column(Integer, ForeignKey("stock_locations.id"), nullable=False)

    # Status
    status = Column(Enum(TransferStatus), default=TransferStatus.DRAFT)

    # Personnel
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Purpose
    reason = Column(Text, nullable=True)

    # Timestamps
    requested_date = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    product = relationship("Product")
    from_location = relationship("StockLocation", foreign_keys=[from_location_id])
    to_location = relationship("StockLocation", foreign_keys=[to_location_id])
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])

    def __repr__(self):
        return f"<StockTransfer {self.transfer_number} - {self.status}>"
