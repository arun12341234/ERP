"""
Analytics Dashboard model - KPI tracking and visualization.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Float, ForeignKey, Enum
from app.core.database import Base
from app.core.config import settings
import enum


class DashboardType(str, enum.Enum):
    EXECUTIVE = "executive"
    SALES = "sales"
    FINANCE = "finance"
    OPERATIONS = "operations"
    MARKETING = "marketing"
    CUSTOM = "custom"


class VisualizationType(str, enum.Enum):
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    TABLE = "table"
    KPI_CARD = "kpi_card"
    GAUGE = "gauge"
    HEATMAP = "heatmap"


class RefreshFrequency(str, enum.Enum):
    REALTIME = "realtime"
    EVERY_MINUTE = "every_minute"
    EVERY_HOUR = "every_hour"
    DAILY = "daily"
    WEEKLY = "weekly"
    MANUAL = "manual"


class AnalyticsDashboard(Base):
    __tablename__ = "analytics_dashboards"

    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(String, unique=True, index=True, nullable=False)

    # Dashboard details
    dashboard_name = Column(String, nullable=False)
    dashboard_type = Column(Enum(DashboardType), nullable=False)
    description = Column(Text, nullable=True)

    # Layout (JSON)
    layout_config = Column(Text, nullable=False)  # JSON object defining grid layout

    # Widgets/KPIs (JSON array)
    widgets = Column(Text, nullable=False)  # JSON array of widget configurations

    # Data sources
    data_sources = Column(Text, nullable=True)  # JSON array of data source configs

    # Refresh settings
    refresh_frequency = Column(Enum(RefreshFrequency), default=RefreshFrequency.EVERY_HOUR)
    last_refreshed_at = Column(DateTime, nullable=True)
    next_refresh_at = Column(DateTime, nullable=True)

    # Access control
    is_public = Column(Integer, default=0)  # boolean as int
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    shared_with = Column(Text, nullable=True)  # JSON array of user IDs

    # Status
    is_active = Column(Integer, default=1)  # boolean as int
    is_published = Column(Integer, default=0)  # boolean as int

    # Filters (default filters applied)
    default_filters = Column(Text, nullable=True)  # JSON object
    date_range = Column(String, default="last_30_days")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<AnalyticsDashboard {self.dashboard_name}>"


class KPIMetric(Base):
    __tablename__ = "kpi_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(String, unique=True, index=True, nullable=False)

    # Metric details
    metric_name = Column(String, nullable=False)
    metric_category = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    # Value
    current_value = Column(Float, nullable=False)
    previous_value = Column(Float, nullable=True)
    target_value = Column(Float, nullable=True)

    # Change metrics
    change_value = Column(Float, default=0.0)
    change_percentage = Column(Float, default=0.0)
    is_improvement = Column(Integer, nullable=True)  # 1=up is good, 0=down is good

    # Time period
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    comparison_period_start = Column(Date, nullable=True)
    comparison_period_end = Column(Date, nullable=True)

    # Visualization
    visualization_type = Column(Enum(VisualizationType), nullable=True)
    chart_data = Column(Text, nullable=True)  # JSON for trend data

    # Data source
    data_source_query = Column(Text, nullable=True)
    calculation_formula = Column(String, nullable=True)

    # Alert thresholds
    warning_threshold = Column(Float, nullable=True)
    critical_threshold = Column(Float, nullable=True)
    is_threshold_breached = Column(Integer, default=0)  # boolean as int

    # Formatting
    unit = Column(String, nullable=True)  # $, %, units, etc.
    decimal_places = Column(Integer, default=2)
    prefix = Column(String, nullable=True)
    suffix = Column(String, nullable=True)

    # Timestamps
    calculated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<KPIMetric {self.metric_name}: {self.current_value}>"
