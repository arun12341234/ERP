"""
Document Digitization model - OCR and document processing.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum
from app.core.database import Base
from app.core.config import settings
import enum


class DocumentType(str, enum.Enum):
    INVOICE = "invoice"
    RECEIPT = "receipt"
    CONTRACT = "contract"
    ID_CARD = "id_card"
    BANK_STATEMENT = "bank_statement"
    TAX_DOCUMENT = "tax_document"
    PURCHASE_ORDER = "purchase_order"
    DELIVERY_NOTE = "delivery_note"
    OTHER = "other"


class ProcessingStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"


class DocumentDigitization(Base):
    __tablename__ = "document_digitizations"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, unique=True, index=True, nullable=False)

    # Document details
    document_type = Column(Enum(DocumentType), nullable=False)
    document_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Upload
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size_bytes = Column(Integer, default=0)
    file_format = Column(String, nullable=True)  # pdf, jpg, png, etc.

    # Status
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.UPLOADED)

    # OCR Processing
    ocr_engine = Column(String, nullable=True)  # tesseract, google_vision, aws_textract
    ocr_language = Column(String, default="eng")
    ocr_confidence = Column(Float, nullable=True)  # 0-100

    # Extracted data
    extracted_text = Column(Text, nullable=True)
    extracted_data = Column(Text, nullable=True)  # JSON object with structured data
    entities_detected = Column(Text, nullable=True)  # JSON array

    # AI/ML Processing
    classification_confidence = Column(Float, nullable=True)
    suggested_document_type = Column(String, nullable=True)

    # Processing metrics
    processing_started_at = Column(DateTime, nullable=True)
    processing_completed_at = Column(DateTime, nullable=True)
    processing_duration_ms = Column(Integer, default=0)

    # Page information
    page_count = Column(Integer, default=1)
    pages_processed = Column(Integer, default=0)

    # Reference
    reference_type = Column(String, nullable=True)  # invoice, purchase_order, etc.
    reference_id = Column(Integer, nullable=True)

    # Verification
    is_verified = Column(Integer, default=0)  # boolean as int
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    verification_notes = Column(Text, nullable=True)

    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

    # Uploaded by
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Tags and metadata
    tags = Column(Text, nullable=True)  # JSON array
    metadata = Column(Text, nullable=True)  # JSON object

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<DocumentDigitization {self.document_id} - {self.document_type}>"
