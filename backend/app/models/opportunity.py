"""
Opportunity model - sales opportunities from leads.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float, Date
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
from app.core.config import settings


class OpportunityStage(str, enum.Enum):
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)

    # Basic info
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Links
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Opportunity details
    stage = Column(Enum(OpportunityStage), default=OpportunityStage.PROSPECTING, index=True)
    probability = Column(Integer, default=10)  # 0-100%
    amount = Column(Float, default=0.0)
    expected_close_date = Column(Date, nullable=True)

    # Scoring
    score = Column(Integer, default=0)  # Opportunity score

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    # Multi-tenant
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    lead = relationship("Lead", back_populates="opportunities")
    customer = relationship("Customer", back_populates="opportunities")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    quotes = relationship("Quote", back_populates="opportunity")

    def __repr__(self):
        return f"<Opportunity {self.name} - {self.stage}>"
