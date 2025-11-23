"""
Lead model - for lead capture, qualification, and assignment.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
from app.core.config import settings


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    REJECTED = "rejected"
    CONVERTED = "converted"


class LeadSource(str, enum.Enum):
    WEBSITE = "website"
    REFERRAL = "referral"
    CAMPAIGN = "campaign"
    COLD_CALL = "cold_call"
    OTHER = "other"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)

    # Basic info
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, index=True, nullable=False)
    phone = Column(String, nullable=True)
    company = Column(String, nullable=True)
    job_title = Column(String, nullable=True)

    # Lead details
    source = Column(Enum(LeadSource), default=LeadSource.WEBSITE)
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW, index=True)
    score = Column(Integer, default=0)  # 0-100 qualification score
    notes = Column(Text, nullable=True)

    # Assignment
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    qualified_at = Column(DateTime, nullable=True)
    converted_at = Column(DateTime, nullable=True)

    # Multi-tenant
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    opportunities = relationship("Opportunity", back_populates="lead")

    def __repr__(self):
        return f"<Lead {self.first_name} {self.last_name} - {self.status}>"
