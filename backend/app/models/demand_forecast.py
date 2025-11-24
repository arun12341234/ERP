"""
Demand Forecast model - demand forecasting and prediction.
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Float, ForeignKey, Enum
from app.core.database import Base
from app.core.config import settings
import enum


class ForecastMethod(str, enum.Enum):
    MOVING_AVERAGE = "moving_average"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    LINEAR_REGRESSION = "linear_regression"
    MACHINE_LEARNING = "machine_learning"
    MANUAL = "manual"


class DemandForecast(Base):
    __tablename__ = "demand_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    forecast_number = Column(String, unique=True, index=True, nullable=False)

    # Product
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Forecast period
    forecast_date = Column(Date, nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    # Forecast method
    forecast_method = Column(Enum(ForecastMethod), nullable=False)

    # Forecast data
    forecasted_quantity = Column(Float, nullable=False)
    confidence_level = Column(Float, default=0.0)  # 0-100 percentage

    # Historical data used
    historical_sales = Column(Float, default=0.0)
    historical_periods = Column(Integer, default=0)

    # Actual vs forecast (filled after period)
    actual_quantity = Column(Float, nullable=True)
    forecast_accuracy = Column(Float, nullable=True)  # Percentage

    # Notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<DemandForecast {self.forecast_number}>"
