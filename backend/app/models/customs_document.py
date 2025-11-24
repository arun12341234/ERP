"""
Customs Document model - import/export documentation.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class CustomsDocumentType(str, enum.Enum):
    COMMERCIAL_INVOICE = "commercial_invoice"
    PACKING_LIST = "packing_list"
    BILL_OF_LADING = "bill_of_lading"
    CERTIFICATE_OF_ORIGIN = "certificate_of_origin"
    EXPORT_DECLARATION = "export_declaration"
    IMPORT_DECLARATION = "import_declaration"
    CUSTOMS_CLEARANCE = "customs_clearance"


class CustomsDocumentStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    CLEARED = "cleared"


class CustomsDocument(Base):
    __tablename__ = "customs_documents"

    id = Column(Integer, primary_key=True, index=True)
    document_number = Column(String, unique=True, index=True, nullable=False)

    # Shipment reference
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=True)
    logistics_request_id = Column(Integer, ForeignKey("logistics_requests.id"), nullable=True)

    # Document details
    document_type = Column(Enum(CustomsDocumentType), nullable=False)
    document_date = Column(Date, nullable=False)

    # Trade details
    export_country = Column(String, nullable=True)
    import_country = Column(String, nullable=True)
    incoterm = Column(String, nullable=True)  # e.g., "FOB", "CIF", "EXW"

    # Cargo details
    hs_code = Column(String, nullable=True)  # Harmonized System code
    cargo_description = Column(Text, nullable=False)
    cargo_value = Column(Integer, default=0)  # in cents
    currency = Column(String, default="USD")

    # Status
    status = Column(Enum(CustomsDocumentStatus), default=CustomsDocumentStatus.DRAFT)

    # Customs
    customs_reference = Column(String, nullable=True)
    customs_authority = Column(String, nullable=True)
    submission_date = Column(Date, nullable=True)
    clearance_date = Column(Date, nullable=True)

    # Documents (file paths or URLs)
    document_file = Column(String, nullable=True)
    supporting_documents = Column(Text, nullable=True)  # JSON array

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<CustomsDocument {self.document_number}>"
