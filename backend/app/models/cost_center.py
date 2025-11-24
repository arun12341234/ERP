"""
Cost Center model - cost center definition and accounting.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from app.core.database import Base
from app.core.config import settings


class CostCenter(Base):
    __tablename__ = "cost_centers"

    id = Column(Integer, primary_key=True, index=True)
    cost_center_code = Column(String, unique=True, index=True, nullable=False)
    cost_center_name = Column(String, nullable=False)

    # Details
    description = Column(Text, nullable=True)
    department = Column(String, nullable=True)

    # Hierarchy
    parent_cost_center_id = Column(Integer, nullable=True)

    # Manager
    manager_name = Column(String, nullable=True)
    manager_id = Column(Integer, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<CostCenter {self.cost_center_code} - {self.cost_center_name}>"
