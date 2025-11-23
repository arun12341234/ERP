"""
Bill of Materials (BOM) model - defines product composition.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings


class BOMItem(Base):
    __tablename__ = "bom_items"

    id = Column(Integer, primary_key=True, index=True)

    # Parent product (finished good)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Component/material
    component_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Quantity
    quantity = Column(Float, nullable=False)
    unit = Column(String, default="pcs")

    # Scrap/waste factor
    scrap_percentage = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    product = relationship("Product", foreign_keys=[product_id], back_populates="bom_items")
    component = relationship("Product", foreign_keys=[component_id])

    def __repr__(self):
        return f"<BOMItem {self.product_id} -> {self.component_id}>"
