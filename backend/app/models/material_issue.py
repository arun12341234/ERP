"""
Material Issue model - materials issued to production.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class IssueStatus(str, enum.Enum):
    PENDING = "pending"
    ISSUED = "issued"
    RETURNED = "returned"
    CANCELLED = "cancelled"


class MaterialIssue(Base):
    __tablename__ = "material_issues"

    id = Column(Integer, primary_key=True, index=True)
    issue_number = Column(String, unique=True, index=True, nullable=False)

    # Work order
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)

    # Product/Material
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Stock location
    location_id = Column(Integer, ForeignKey("stock_locations.id"), nullable=True)

    # Quantities
    quantity_requested = Column(Float, nullable=False)
    quantity_issued = Column(Float, default=0.0)
    quantity_returned = Column(Float, default=0.0)

    # Cost
    unit_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)

    # Status
    status = Column(Enum(IssueStatus), default=IssueStatus.PENDING)

    # Issued by
    issued_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    issued_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    work_order = relationship("WorkOrder")
    product = relationship("Product")

    def __repr__(self):
        return f"<MaterialIssue {self.issue_number}>"
