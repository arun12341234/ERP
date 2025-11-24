"""
Fixed Asset model - asset management and tracking.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Enum, Boolean
from app.core.database import Base
from app.core.config import settings
import enum


class AssetStatus(str, enum.Enum):
    ACTIVE = "active"
    DISPOSED = "disposed"
    FULLY_DEPRECIATED = "fully_depreciated"
    UNDER_MAINTENANCE = "under_maintenance"


class DepreciationMethod(str, enum.Enum):
    STRAIGHT_LINE = "straight_line"
    DECLINING_BALANCE = "declining_balance"
    UNITS_OF_PRODUCTION = "units_of_production"


class FixedAsset(Base):
    __tablename__ = "fixed_assets"

    id = Column(Integer, primary_key=True, index=True)
    asset_number = Column(String, unique=True, index=True, nullable=False)

    # Asset details
    asset_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False)  # e.g., "Buildings", "Machinery", "Vehicles"

    # Acquisition
    acquisition_date = Column(Date, nullable=False)
    acquisition_cost = Column(Integer, nullable=False)  # in cents
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)

    # Location
    location = Column(String, nullable=True)
    department = Column(String, nullable=True)
    custodian = Column(String, nullable=True)

    # Depreciation
    depreciation_method = Column(Enum(DepreciationMethod), default=DepreciationMethod.STRAIGHT_LINE)
    useful_life_years = Column(Integer, nullable=False)
    salvage_value = Column(Integer, default=0)  # in cents
    accumulated_depreciation = Column(Integer, default=0)  # in cents
    net_book_value = Column(Integer, default=0)  # in cents

    # GL Accounts
    asset_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True)
    depreciation_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True)
    accumulated_depreciation_account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=True)

    # Status
    status = Column(Enum(AssetStatus), default=AssetStatus.ACTIVE)

    # Disposal
    disposal_date = Column(Date, nullable=True)
    disposal_proceeds = Column(Integer, default=0)  # in cents

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<FixedAsset {self.asset_number} - {self.asset_name}>"
