"""
Production Execution model - production activity tracking.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings


class ProductionExecution(Base):
    __tablename__ = "production_executions"

    id = Column(Integer, primary_key=True, index=True)

    # Work order
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)

    # Shopfloor job (optional)
    job_id = Column(Integer, ForeignKey("shopfloor_jobs.id"), nullable=True)

    # Production details
    quantity_produced = Column(Float, nullable=False)
    quantity_good = Column(Float, default=0.0)
    quantity_rejected = Column(Float, default=0.0)

    # Time
    execution_date = Column(DateTime, nullable=False)
    duration_hours = Column(Float, default=0.0)

    # Operator
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Machine
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    work_order = relationship("WorkOrder")
    operator = relationship("User")
    machine = relationship("Machine")

    def __repr__(self):
        return f"<ProductionExecution WO:{self.work_order_id}>"
