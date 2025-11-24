"""
Risk Assessment model - enterprise risk management and analysis.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Float, ForeignKey, Enum
from app.core.database import Base
from app.core.config import settings
import enum


class RiskCategory(str, enum.Enum):
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    STRATEGIC = "strategic"
    COMPLIANCE = "compliance"
    CYBERSECURITY = "cybersecurity"
    REPUTATION = "reputational"
    MARKET = "market"
    ENVIRONMENTAL = "environmental"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskStatus(str, enum.Enum):
    IDENTIFIED = "identified"
    ANALYZING = "analyzing"
    MITIGATING = "mitigating"
    MONITORING = "monitoring"
    CLOSED = "closed"
    ACCEPTED = "accepted"


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(String, unique=True, index=True, nullable=False)

    # Risk details
    risk_title = Column(String, nullable=False)
    risk_category = Column(Enum(RiskCategory), nullable=False)
    description = Column(Text, nullable=False)

    # Assessment
    likelihood_score = Column(Integer, nullable=False)  # 1-5
    impact_score = Column(Integer, nullable=False)  # 1-5
    risk_score = Column(Integer, nullable=False)  # likelihood × impact
    risk_level = Column(Enum(RiskLevel), nullable=False)

    # Status
    status = Column(Enum(RiskStatus), default=RiskStatus.IDENTIFIED)

    # Impact analysis
    financial_impact = Column(Integer, default=0)  # in cents
    operational_impact = Column(Text, nullable=True)
    affected_processes = Column(Text, nullable=True)  # JSON array

    # Timeline
    identified_date = Column(Date, nullable=False)
    target_resolution_date = Column(Date, nullable=True)
    actual_resolution_date = Column(Date, nullable=True)

    # Ownership
    risk_owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    identified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Mitigation strategy
    mitigation_strategy = Column(Text, nullable=True)
    mitigation_actions = Column(Text, nullable=True)  # JSON array
    mitigation_cost = Column(Integer, default=0)  # in cents
    mitigation_status = Column(String, nullable=True)

    # Control measures
    existing_controls = Column(Text, nullable=True)
    proposed_controls = Column(Text, nullable=True)
    control_effectiveness = Column(String, nullable=True)  # low, medium, high

    # Residual risk (after mitigation)
    residual_likelihood_score = Column(Integer, nullable=True)
    residual_impact_score = Column(Integer, nullable=True)
    residual_risk_score = Column(Integer, nullable=True)
    residual_risk_level = Column(Enum(RiskLevel), nullable=True)

    # Review
    last_reviewed_at = Column(Date, nullable=True)
    next_review_date = Column(Date, nullable=True)
    review_frequency_days = Column(Integer, default=90)

    # Escalation
    is_escalated = Column(Integer, default=0)  # boolean as int
    escalated_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    escalation_date = Column(DateTime, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)
    lessons_learned = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<RiskAssessment {self.risk_id} - {self.risk_level}>"
