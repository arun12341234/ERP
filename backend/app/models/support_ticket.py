"""
Support Ticket model - customer support and issue tracking.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
from app.core.config import settings


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(str, enum.Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    PENDING_CUSTOMER = "pending_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ESCALATED = "escalated"


class TicketCategory(str, enum.Enum):
    TECHNICAL = "technical"
    BILLING = "billing"
    GENERAL = "general"
    COMPLAINT = "complaint"
    FEATURE_REQUEST = "feature_request"


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String, unique=True, index=True, nullable=False)

    # Links
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Ticket details
    category = Column(Enum(TicketCategory), default=TicketCategory.GENERAL)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM, index=True)
    status = Column(Enum(TicketStatus), default=TicketStatus.NEW, index=True)

    subject = Column(String, nullable=False)
    description = Column(Text, nullable=False)

    # Resolution
    resolution_notes = Column(Text, nullable=True)
    resolved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Escalation
    is_escalated = Column(Enum, default=False)
    escalated_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    escalation_reason = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    escalated_at = Column(DateTime, nullable=True)

    # Multi-tenant
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    customer = relationship("Customer", back_populates="tickets")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    resolved_by = relationship("User", foreign_keys=[resolved_by_id])
    escalated_to = relationship("User", foreign_keys=[escalated_to_id])

    def __repr__(self):
        return f"<SupportTicket {self.ticket_number} - {self.status}>"
