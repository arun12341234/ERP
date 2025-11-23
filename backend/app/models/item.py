"""Item model - sample resource for CRUD operations."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Optional: Multi-tenant field (only used if ENABLE_TENANCY=true)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    owner = relationship("User", back_populates="items")

    def __repr__(self):
        return f"<Item {self.title}>"
