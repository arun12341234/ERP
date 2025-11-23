"""
Quality Check Production model - in-process quality checks.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class QCResult(str, enum.Enum):
    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL_PASS = "conditional_pass"
    PENDING = "pending"


class QualityCheckProduction(Base):
    __tablename__ = "quality_checks_production"

    id = Column(Integer, primary_key=True, index=True)
    check_number = Column(String, unique=True, index=True, nullable=False)

    # Work order
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)

    # Production execution (optional)
    execution_id = Column(Integer, ForeignKey("production_executions.id"), nullable=True)

    # Check details
    check_type = Column(String, nullable=False)
    check_point = Column(String, nullable=True)  # e.g., "Start of production", "Mid-process"

    # Sample
    sample_size = Column(Float, nullable=False)
    quantity_passed = Column(Float, default=0.0)
    quantity_failed = Column(Float, default=0.0)

    # Result
    result = Column(Enum(QCResult), default=QCResult.PENDING)
    defects_found = Column(Text, nullable=True)

    # Inspector
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    inspection_date = Column(DateTime, nullable=False)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    work_order = relationship("WorkOrder")
    inspector = relationship("User")

    def __repr__(self):
        return f"<QualityCheckProduction {self.check_number}>"
