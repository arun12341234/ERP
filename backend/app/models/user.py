"""User model with optional tenant support."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default="user")  # admin, user, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Optional: Multi-tenant field (only used if ENABLE_TENANCY=true)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"


# Optional Tenant model (only created if ENABLE_TENANCY=true)
if settings.ENABLE_TENANCY:
    class Tenant(Base):
        __tablename__ = "tenants"

        id = Column(Integer, primary_key=True, index=True)
        name = Column(String, nullable=False)
        domain = Column(String, unique=True, index=True)
        is_active = Column(Boolean, default=True)
        created_at = Column(DateTime, default=datetime.utcnow)

        def __repr__(self):
            return f"<Tenant {self.name}>"
