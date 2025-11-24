"""
API Integration model - third-party API configuration and monitoring.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from app.core.database import Base
from app.core.config import settings
import enum


class IntegrationStatus(str, enum.Enum):
    DRAFT = "draft"
    TESTING = "testing"
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    DEPRECATED = "deprecated"


class AuthType(str, enum.Enum):
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basic_auth"
    JWT = "jwt"
    BEARER_TOKEN = "bearer_token"
    NONE = "none"


class APIIntegration(Base):
    __tablename__ = "api_integrations"

    id = Column(Integer, primary_key=True, index=True)
    integration_id = Column(String, unique=True, index=True, nullable=False)

    # Integration details
    integration_name = Column(String, nullable=False)
    provider_name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # API Configuration
    base_url = Column(String, nullable=False)
    api_version = Column(String, nullable=True)
    documentation_url = Column(String, nullable=True)

    # Authentication
    auth_type = Column(Enum(AuthType), nullable=False)
    api_key = Column(String, nullable=True)  # Encrypted
    api_secret = Column(String, nullable=True)  # Encrypted
    access_token = Column(String, nullable=True)  # Encrypted
    refresh_token = Column(String, nullable=True)  # Encrypted
    token_expires_at = Column(DateTime, nullable=True)

    # Headers (JSON)
    custom_headers = Column(Text, nullable=True)  # JSON object

    # Status
    status = Column(Enum(IntegrationStatus), default=IntegrationStatus.DRAFT)
    is_active = Column(Integer, default=0)  # boolean as int

    # Rate limiting
    rate_limit_requests = Column(Integer, nullable=True)
    rate_limit_period_seconds = Column(Integer, default=60)
    current_usage = Column(Integer, default=0)

    # Testing
    last_test_at = Column(DateTime, nullable=True)
    last_test_status = Column(String, nullable=True)
    last_test_response = Column(Text, nullable=True)

    # Deployment
    deployed_at = Column(DateTime, nullable=True)
    deployed_by_id = Column(Integer, nullable=True)

    # Monitoring
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    average_response_time_ms = Column(Integer, default=0)
    last_request_at = Column(DateTime, nullable=True)

    # Error tracking
    last_error_message = Column(Text, nullable=True)
    last_error_at = Column(DateTime, nullable=True)
    consecutive_failures = Column(Integer, default=0)

    # Webhooks
    webhook_url = Column(String, nullable=True)
    webhook_secret = Column(String, nullable=True)  # Encrypted

    # Configuration
    timeout_seconds = Column(Integer, default=30)
    retry_count = Column(Integer, default=3)
    retry_delay_seconds = Column(Integer, default=5)

    # Metadata
    tags = Column(Text, nullable=True)  # JSON array
    metadata = Column(Text, nullable=True)  # JSON object

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<APIIntegration {self.integration_name} - {self.provider_name}>"
