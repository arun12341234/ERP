"""
Regulatory Compliance model - compliance tracking and validation.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Enum
from app.core.database import Base
from app.core.config import settings
import enum


class ComplianceType(str, enum.Enum):
    GDPR = "gdpr"
    SOX = "sox"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    SOC2 = "soc2"
    CCPA = "ccpa"
    LOCAL_TAX = "local_tax"
    LABOR_LAW = "labor_law"
    ENVIRONMENTAL = "environmental"
    CUSTOM = "custom"


class ComplianceStatus(str, enum.Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    PENDING_REVIEW = "pending_review"
    EXPIRED = "expired"
    NOT_APPLICABLE = "not_applicable"


class RegulatoryCompliance(Base):
    __tablename__ = "regulatory_compliance"

    id = Column(Integer, primary_key=True, index=True)
    compliance_id = Column(String, unique=True, index=True, nullable=False)

    # Compliance details
    compliance_type = Column(Enum(ComplianceType), nullable=False)
    regulation_name = Column(String, nullable=False)
    regulation_code = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    # Status
    status = Column(Enum(ComplianceStatus), nullable=False)
    compliance_score = Column(Integer, default=0)  # 0-100

    # Requirements
    total_requirements = Column(Integer, default=0)
    met_requirements = Column(Integer, default=0)
    pending_requirements = Column(Integer, default=0)
    failed_requirements = Column(Integer, default=0)

    # Checklist (JSON array of requirement items)
    checklist = Column(Text, nullable=False)  # JSON array

    # Assessment
    last_assessment_date = Column(Date, nullable=True)
    next_assessment_date = Column(Date, nullable=True)
    assessment_frequency_days = Column(Integer, default=365)

    # Assessor
    assessed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assessor_name = Column(String, nullable=True)
    assessor_organization = Column(String, nullable=True)

    # Evidence
    evidence_documents = Column(Text, nullable=True)  # JSON array of document IDs
    supporting_documentation = Column(Text, nullable=True)  # JSON array

    # Remediation
    remediation_plan = Column(Text, nullable=True)
    remediation_deadline = Column(Date, nullable=True)
    remediation_owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    remediation_status = Column(String, nullable=True)

    # Gaps
    identified_gaps = Column(Text, nullable=True)  # JSON array
    gap_analysis_notes = Column(Text, nullable=True)

    # Risk
    non_compliance_risk = Column(String, nullable=True)  # low, medium, high, critical
    potential_penalties = Column(Integer, default=0)  # in cents

    # Certification
    is_certified = Column(Integer, default=0)  # boolean as int
    certification_number = Column(String, nullable=True)
    certification_date = Column(Date, nullable=True)
    certification_expiry = Column(Date, nullable=True)
    certification_body = Column(String, nullable=True)

    # Monitoring
    monitoring_enabled = Column(Integer, default=1)  # boolean as int
    last_monitored_at = Column(DateTime, nullable=True)

    # Reporting
    reporting_frequency = Column(String, nullable=True)  # monthly, quarterly, annually
    last_report_date = Column(Date, nullable=True)
    next_report_due = Column(Date, nullable=True)

    # Responsible party
    compliance_officer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    department = Column(String, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)
    auditor_comments = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<RegulatoryCompliance {self.regulation_name} - {self.status}>"
