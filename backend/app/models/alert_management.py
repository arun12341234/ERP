"""
Alert Management model - system alerts and notifications.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from app.core.database import Base
from app.core.config import settings
import enum


class AlertType(str, enum.Enum):
    SYSTEM = "system"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BUSINESS = "business"
    COMPLIANCE = "compliance"
    THRESHOLD = "threshold"
    ERROR = "error"


class AlertSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(str, enum.Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"
    IGNORED = "ignored"


class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SLACK = "slack"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


class AlertManagement(Base):
    __tablename__ = "alert_management"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String, unique=True, index=True, nullable=False)

    # Alert details
    alert_type = Column(Enum(AlertType), nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)

    # Source
    source_system = Column(String, nullable=True)
    source_component = Column(String, nullable=True)
    source_entity_type = Column(String, nullable=True)
    source_entity_id = Column(Integer, nullable=True)

    # Status
    status = Column(Enum(AlertStatus), default=AlertStatus.OPEN)

    # Rule-based
    rule_id = Column(String, nullable=True, index=True)
    rule_name = Column(String, nullable=True)
    rule_condition = Column(Text, nullable=True)

    # Threshold breach
    metric_name = Column(String, nullable=True)
    threshold_value = Column(String, nullable=True)
    actual_value = Column(String, nullable=True)

    # Assignment
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_at = Column(DateTime, nullable=True)

    # Acknowledgment
    acknowledged_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)

    # Resolution
    resolved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    resolution_time_minutes = Column(Integer, nullable=True)

    # Notification
    notification_channels = Column(Text, nullable=True)  # JSON array
    notification_sent_at = Column(DateTime, nullable=True)
    notification_recipients = Column(Text, nullable=True)  # JSON array

    # Escalation
    is_escalated = Column(Integer, default=0)  # boolean as int
    escalation_level = Column(Integer, default=0)
    escalated_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    escalated_at = Column(DateTime, nullable=True)

    # Auto-resolution
    is_auto_resolvable = Column(Integer, default=0)  # boolean as int
    auto_resolved = Column(Integer, default=0)  # boolean as int

    # Related alerts
    parent_alert_id = Column(String, nullable=True)
    related_alert_ids = Column(Text, nullable=True)  # JSON array

    # Frequency (for recurring alerts)
    occurrence_count = Column(Integer, default=1)
    first_occurred_at = Column(DateTime, default=datetime.utcnow)
    last_occurred_at = Column(DateTime, default=datetime.utcnow)

    # Priority
    priority = Column(Integer, default=3)  # 1-5, 1=highest

    # Context data
    context_data = Column(Text, nullable=True)  # JSON object
    error_stack_trace = Column(Text, nullable=True)

    # Tags
    tags = Column(Text, nullable=True)  # JSON array

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<AlertManagement {self.alert_id} - {self.severity}>"
