"""
Finished Goods Receipt model - finished goods receiving from production.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class FGReceiptStatus(str, enum.Enum):
    PENDING = "pending"
    RECEIVED = "received"
    PUT_AWAY = "put_away"
    CANCELLED = "cancelled"


class FinishedGoodsReceipt(Base):
    __tablename__ = "finished_goods_receipts"

    id = Column(Integer, primary_key=True, index=True)
    receipt_number = Column(String, unique=True, index=True, nullable=False)

    # Work order
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)

    # Product
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Quantities
    quantity_received = Column(Float, nullable=False)

    # Location
    location_id = Column(Integer, ForeignKey("stock_locations.id"), nullable=True)

    # Status
    status = Column(Enum(FGReceiptStatus), default=FGReceiptStatus.PENDING)

    # Received by
    received_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    received_date = Column(DateTime, nullable=True)

    # Cost
    unit_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    work_order = relationship("WorkOrder")
    product = relationship("Product")
    location = relationship("StockLocation")

    def __repr__(self):
        return f"<FinishedGoodsReceipt {self.receipt_number}>"
