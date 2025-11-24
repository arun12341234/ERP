"""
Audit Log model - system audit trail and compliance logging.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from app.core.database import Base
from app.core.config import settings
import enum


class AuditAction(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    APPROVE = "approve"
    REJECT = "reject"
    POST = "post"
    REVERSE = "reverse"


class AuditSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    username = Column(String, nullable=True)
    user_ip = Column(String, nullable=True)

    # Action
    action = Column(Enum(AuditAction), nullable=False)
    severity = Column(Enum(AuditSeverity), default=AuditSeverity.INFO)

    # Entity
    entity_type = Column(String, nullable=False)  # e.g., "Invoice", "JournalEntry"
    entity_id = Column(Integer, nullable=True)
    entity_identifier = Column(String, nullable=True)  # e.g., invoice_number, entry_number

    # Description
    description = Column(Text, nullable=False)

    # Changes (JSON or text)
    changes = Column(Text, nullable=True)  # Can store JSON string of before/after values

    # Request details
    request_method = Column(String, nullable=True)
    request_path = Column(String, nullable=True)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<AuditLog {self.timestamp} - {self.action} {self.entity_type}>"
