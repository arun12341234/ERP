"""
Role Assignment model - user roles and access rights management.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class RoleType(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    SUPERVISOR = "supervisor"
    EMPLOYEE = "employee"
    ACCOUNTANT = "accountant"
    SALES_REP = "sales_rep"
    WAREHOUSE_STAFF = "warehouse_staff"
    CUSTOMER = "customer"
    VENDOR = "vendor"
    CUSTOM = "custom"


class AssignmentStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    EXPIRED = "expired"


class RoleAssignment(Base):
    __tablename__ = "role_assignments"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(String, unique=True, index=True, nullable=False)

    # User
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Role
    role_type = Column(Enum(RoleType), nullable=False)
    role_name = Column(String, nullable=False)
    role_description = Column(Text, nullable=True)

    # Permissions (JSON)
    permissions = Column(Text, nullable=False)  # JSON object of permissions
    access_modules = Column(Text, nullable=True)  # JSON array of module names

    # Status
    status = Column(Enum(AssignmentStatus), default=AssignmentStatus.ACTIVE)

    # Assignment details
    assigned_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)

    # Expiry (optional)
    expires_at = Column(DateTime, nullable=True)

    # Revocation
    revoked_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    revocation_reason = Column(Text, nullable=True)

    # Restrictions
    ip_restrictions = Column(Text, nullable=True)  # JSON array
    time_restrictions = Column(Text, nullable=True)  # JSON object

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self):
        return f"<RoleAssignment {self.assignment_id} - {self.role_type}>"
