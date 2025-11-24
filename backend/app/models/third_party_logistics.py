"""
Third Party Logistics model - 3PL integration and synchronization.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from app.core.database import Base
from app.core.config import settings
import enum


class ThirdPartyLogisticsStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SYNCING = "syncing"
    ERROR = "error"


class ThirdPartyLogistics(Base):
    __tablename__ = "third_party_logistics"

    id = Column(Integer, primary_key=True, index=True)

    # 3PL Provider details
    provider_name = Column(String, nullable=False, index=True)
    provider_code = Column(String, unique=True, index=True, nullable=False)
    provider_type = Column(String, nullable=True)  # e.g., "warehouse", "freight", "full_service"

    # Integration details
    api_endpoint = Column(String, nullable=True)
    api_key = Column(String, nullable=True)  # Encrypted
    integration_method = Column(String, nullable=True)  # e.g., "api", "edi", "sftp"

    # Status
    status = Column(Enum(ThirdPartyLogisticsStatus), default=ThirdPartyLogisticsStatus.ACTIVE)
    is_active = Column(Integer, default=1)  # boolean as int

    # Synchronization
    last_sync_timestamp = Column(DateTime, nullable=True)
    last_sync_status = Column(String, nullable=True)
    sync_frequency_minutes = Column(Integer, default=60)

    # Data mapping (JSON configuration)
    field_mapping = Column(Text, nullable=True)
    sync_configuration = Column(Text, nullable=True)

    # Contact information
    contact_person = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<ThirdPartyLogistics {self.provider_name} ({self.provider_code})>"
