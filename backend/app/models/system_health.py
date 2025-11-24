"""
System Health model - infrastructure monitoring and alerting.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Enum
from app.core.database import Base
from app.core.config import settings
import enum


class HealthStatus(str, enum.Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    DOWN = "down"


class ComponentType(str, enum.Enum):
    API = "api"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    STORAGE = "storage"
    EXTERNAL_SERVICE = "external_service"
    WORKER = "worker"


class SystemHealthCheck(Base):
    __tablename__ = "system_health_checks"

    id = Column(Integer, primary_key=True, index=True)
    check_id = Column(String, unique=True, index=True, nullable=False)

    # Component details
    component_type = Column(Enum(ComponentType), nullable=False)
    component_name = Column(String, nullable=False, index=True)
    component_url = Column(String, nullable=True)

    # Health status
    status = Column(Enum(HealthStatus), nullable=False)
    previous_status = Column(Enum(HealthStatus), nullable=True)

    # Metrics
    response_time_ms = Column(Integer, nullable=True)
    cpu_usage_percent = Column(Float, nullable=True)
    memory_usage_percent = Column(Float, nullable=True)
    disk_usage_percent = Column(Float, nullable=True)

    # Availability
    uptime_seconds = Column(Integer, nullable=True)
    downtime_seconds = Column(Integer, default=0)
    availability_percent = Column(Float, default=100.0)

    # Error tracking
    error_count = Column(Integer, default=0)
    last_error_message = Column(Text, nullable=True)
    last_error_at = Column(DateTime, nullable=True)

    # Alerts
    is_alert_sent = Column(Integer, default=0)  # boolean as int
    alert_sent_at = Column(DateTime, nullable=True)
    escalated_to = Column(String, nullable=True)

    # Thresholds
    response_time_threshold_ms = Column(Integer, default=5000)
    cpu_threshold_percent = Column(Float, default=80.0)
    memory_threshold_percent = Column(Float, default=80.0)

    # Check metadata
    check_interval_seconds = Column(Integer, default=60)
    last_checked_at = Column(DateTime, nullable=True)
    next_check_at = Column(DateTime, nullable=True)

    # Additional data
    metadata = Column(Text, nullable=True)  # JSON object
    logs = Column(Text, nullable=True)  # Recent log entries

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<SystemHealthCheck {self.component_name} - {self.status}>"
