"""
Data Backup model - automated database backup management.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Enum
from app.core.database import Base
from app.core.config import settings
import enum


class BackupType(str, enum.Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"


class BackupStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RESTORED = "restored"


class BackupStorage(str, enum.Enum):
    LOCAL = "local"
    S3 = "s3"
    AZURE = "azure"
    GCS = "gcs"
    FTP = "ftp"


class DataBackup(Base):
    __tablename__ = "data_backups"

    id = Column(Integer, primary_key=True, index=True)
    backup_id = Column(String, unique=True, index=True, nullable=False)

    # Backup details
    backup_type = Column(Enum(BackupType), nullable=False)
    backup_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Status
    status = Column(Enum(BackupStatus), default=BackupStatus.SCHEDULED)

    # Schedule
    scheduled_at = Column(DateTime, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Storage
    storage_type = Column(Enum(BackupStorage), nullable=False)
    storage_path = Column(String, nullable=True)
    backup_file_name = Column(String, nullable=True)

    # Size and metrics
    backup_size_mb = Column(Float, default=0.0)
    compressed_size_mb = Column(Float, default=0.0)
    compression_ratio = Column(Float, default=1.0)

    # Duration
    duration_seconds = Column(Integer, default=0)

    # Scope
    database_name = Column(String, nullable=True)
    tables_included = Column(Text, nullable=True)  # JSON array
    exclude_tables = Column(Text, nullable=True)  # JSON array

    # Encryption
    is_encrypted = Column(Integer, default=0)  # boolean as int
    encryption_algorithm = Column(String, nullable=True)

    # Verification
    is_verified = Column(Integer, default=0)  # boolean as int
    checksum = Column(String, nullable=True)

    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)

    # Retention
    retention_days = Column(Integer, default=30)
    expires_at = Column(DateTime, nullable=True)
    is_deleted = Column(Integer, default=0)  # boolean as int

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<DataBackup {self.backup_id} - {self.backup_type}>"
