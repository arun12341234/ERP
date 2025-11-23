"""
Quality Inspection model - QC for received goods.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings


class QualityInspection(Base):
    __tablename__ = "quality_inspections"

    id = Column(Integer, primary_key=True, index=True)
    inspection_number = Column(String, unique=True, index=True, nullable=False)

    # GRN reference
    grn_id = Column(Integer, ForeignKey("goods_receipt_notes.id"), nullable=False)

    # Inspection details
    inspected_quantity = Column(Float, nullable=False)
    passed_quantity = Column(Float, default=0.0)
    rejected_quantity = Column(Float, default=0.0)

    # Result
    passed = Column(Boolean, default=False)

    # Inspector
    inspected_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Report
    findings = Column(Text, nullable=True)
    defects = Column(Text, nullable=True)

    # Timestamps
    inspection_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    grn = relationship("GoodsReceiptNote", back_populates="quality_inspections")
    inspected_by = relationship("User")

    def __repr__(self):
        return f"<QualityInspection {self.inspection_number}>"
