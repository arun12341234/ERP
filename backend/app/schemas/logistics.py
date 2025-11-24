"""
Pydantic schemas for Supply Chain & Logistics module.
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


# ============================================================================
# Process 76: Logistics Request Creation
# ============================================================================

class LogisticsRequestCreate(BaseModel):
    sales_order_id: Optional[int] = None
    customer_id: int
    transport_mode: str  # road, rail, air, sea, multimodal
    origin_location: str
    destination_location: str
    pickup_date: date
    delivery_date: date
    total_weight_kg: float
    total_volume_m3: Optional[float] = None
    special_instructions: Optional[str] = None
    estimated_cost: int = 0  # in cents


class LogisticsRequestResponse(BaseModel):
    id: int
    request_number: str
    sales_order_id: Optional[int]
    customer_id: int
    transport_mode: str
    origin_location: str
    destination_location: str
    pickup_date: date
    delivery_date: date
    total_weight_kg: float
    total_volume_m3: Optional[float]
    special_instructions: Optional[str]
    estimated_cost: int
    actual_cost: int
    status: str
    approved_by_id: Optional[int]
    approval_date: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 77: Loading Plan Optimization
# ============================================================================

class LoadingPlanCreate(BaseModel):
    logistics_request_id: int
    vehicle_id: Optional[str] = None
    vehicle_type: Optional[str] = None
    max_capacity_kg: float
    max_volume_m3: Optional[float] = None
    loading_sequence: Optional[str] = None  # JSON
    loading_instructions: Optional[str] = None


class LoadingPlanResponse(BaseModel):
    id: int
    plan_number: str
    logistics_request_id: int
    vehicle_id: Optional[str]
    vehicle_type: Optional[str]
    max_capacity_kg: float
    max_volume_m3: Optional[float]
    planned_weight_kg: float
    planned_volume_m3: float
    capacity_utilization_percent: float
    loading_sequence: Optional[str]
    loading_instructions: Optional[str]
    status: str
    planned_by_id: Optional[int]
    planned_date: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 78: Shipment Dispatch
# ============================================================================

class ShipmentCreate(BaseModel):
    logistics_request_id: int
    loading_plan_id: Optional[int] = None
    carrier_name: Optional[str] = None
    vehicle_number: Optional[str] = None
    driver_name: Optional[str] = None
    driver_contact: Optional[str] = None
    dispatch_date: date
    expected_delivery_date: date


class ShipmentResponse(BaseModel):
    id: int
    shipment_number: str
    tracking_number: Optional[str]
    logistics_request_id: int
    loading_plan_id: Optional[int]
    carrier_name: Optional[str]
    vehicle_number: Optional[str]
    driver_name: Optional[str]
    driver_contact: Optional[str]
    dispatch_date: date
    actual_delivery_date: Optional[date]
    expected_delivery_date: date
    status: str
    dispatched_by_id: Optional[int]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 79: Real-Time Tracking
# ============================================================================

class ShipmentTrackingCreate(BaseModel):
    shipment_id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_description: Optional[str] = None
    status_message: Optional[str] = None
    estimated_arrival: Optional[datetime] = None


class ShipmentTrackingResponse(BaseModel):
    id: int
    shipment_id: int
    tracking_timestamp: datetime
    latitude: Optional[float]
    longitude: Optional[float]
    location_description: Optional[str]
    status_message: Optional[str]
    estimated_arrival: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 80: Delivery Confirmation
# ============================================================================

class DeliveryConfirmationCreate(BaseModel):
    shipment_id: int
    delivered_to_name: str
    delivered_to_contact: Optional[str] = None
    signature_file: Optional[str] = None
    photo_file: Optional[str] = None
    condition_on_delivery: Optional[str] = None
    remarks: Optional[str] = None


class DeliveryConfirmationResponse(BaseModel):
    id: int
    confirmation_number: str
    shipment_id: int
    delivery_date: date
    delivery_time: datetime
    delivered_to_name: str
    delivered_to_contact: Optional[str]
    signature_file: Optional[str]
    photo_file: Optional[str]
    condition_on_delivery: Optional[str]
    is_confirmed: int
    confirmed_by_id: Optional[int]
    remarks: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 81: Freight Invoice Reconciliation
# ============================================================================

class FreightInvoiceCreate(BaseModel):
    shipment_id: int
    carrier_name: str
    invoice_date: date
    due_date: date
    freight_charges: int  # in cents
    fuel_surcharge: int = 0
    handling_charges: int = 0
    other_charges: int = 0


class FreightInvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    shipment_id: int
    carrier_name: str
    invoice_date: date
    due_date: date
    freight_charges: int
    fuel_surcharge: int
    handling_charges: int
    other_charges: int
    total_amount: int
    amount_paid: int
    variance_amount: int
    status: str
    verified_by_id: Optional[int]
    verification_date: Optional[datetime]
    payment_date: Optional[date]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 82: Demand Forecasting
# ============================================================================

class DemandForecastCreate(BaseModel):
    product_id: int
    forecast_period_start: date
    forecast_period_end: date
    forecast_method: str  # moving_average, exponential_smoothing, ml_model
    historical_data: Optional[str] = None  # JSON


class DemandForecastResponse(BaseModel):
    id: int
    forecast_number: str
    product_id: int
    forecast_period_start: date
    forecast_period_end: date
    forecast_method: str
    historical_data: Optional[str]
    forecasted_demand: float
    confidence_level: Optional[float]
    actual_demand: Optional[float]
    accuracy_percent: Optional[float]
    status: str
    created_by_id: Optional[int]
    approved_by_id: Optional[int]
    approval_date: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 83: Route Optimization
# ============================================================================

class RouteOptimizationCreate(BaseModel):
    route_name: str
    start_location: str
    end_location: str
    waypoints: Optional[str] = None  # JSON array
    optimization_criteria: str  # distance, time, cost
    vehicle_type: Optional[str] = None


class RouteOptimizationResponse(BaseModel):
    id: int
    route_number: str
    route_name: str
    start_location: str
    end_location: str
    waypoints: Optional[str]
    optimization_criteria: str
    vehicle_type: Optional[str]
    optimized_route: Optional[str]
    total_distance_km: float
    estimated_time_hours: float
    estimated_cost: int
    fuel_consumption_liters: Optional[float]
    status: str
    optimized_by_id: Optional[int]
    optimization_date: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 84: Carrier Performance Review
# ============================================================================

class CarrierPerformanceCreate(BaseModel):
    carrier_name: str
    review_period_start: date
    review_period_end: date
    total_shipments: int = 0
    on_time_deliveries: int = 0
    damaged_shipments: int = 0
    lost_shipments: int = 0


class CarrierPerformanceResponse(BaseModel):
    id: int
    review_number: str
    carrier_name: str
    review_period_start: date
    review_period_end: date
    total_shipments: int
    on_time_deliveries: int
    damaged_shipments: int
    lost_shipments: int
    on_time_percentage: float
    damage_rate_percentage: float
    loss_rate_percentage: float
    average_rating: Optional[float]
    total_cost: int
    cost_per_shipment: int
    status: str
    reviewed_by_id: Optional[int]
    review_date: Optional[datetime]
    recommendations: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 85: Warehouse Slotting
# ============================================================================

class WarehouseSlotCreate(BaseModel):
    warehouse_location: str
    zone: str
    aisle: str
    rack: str
    shelf: str
    bin: str
    capacity_kg: float
    capacity_m3: Optional[float] = None


class WarehouseSlotResponse(BaseModel):
    id: int
    slot_code: str
    warehouse_location: str
    zone: str
    aisle: str
    rack: str
    shelf: str
    bin: str
    capacity_kg: float
    capacity_m3: Optional[float]
    current_weight_kg: float
    current_volume_m3: float
    utilization_percent: float
    product_id: Optional[int]
    stock_quantity: float
    is_available: int
    last_replenished: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 86: Packaging Request
# ============================================================================

class PackagingRequestCreate(BaseModel):
    sales_order_id: Optional[int] = None
    shipment_id: Optional[int] = None
    product_id: int
    request_date: date
    quantity_to_pack: float
    packaging_type: Optional[str] = None
    packaging_material: Optional[str] = None
    special_handling: Optional[str] = None


class PackagingRequestResponse(BaseModel):
    id: int
    request_number: str
    sales_order_id: Optional[int]
    shipment_id: Optional[int]
    product_id: int
    request_date: date
    quantity_to_pack: float
    quantity_packed: float
    packaging_type: Optional[str]
    packaging_material: Optional[str]
    special_handling: Optional[str]
    length_cm: Optional[float]
    width_cm: Optional[float]
    height_cm: Optional[float]
    weight_kg: Optional[float]
    status: str
    packed_by_id: Optional[int]
    packed_date: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 87: Returns & Reverse Logistics
# ============================================================================

class ReturnRequestCreate(BaseModel):
    sales_order_id: Optional[int] = None
    shipment_id: Optional[int] = None
    invoice_id: Optional[int] = None
    customer_id: int
    product_id: int
    request_date: date
    return_reason: str  # defective, wrong_item, damaged, etc.
    reason_description: Optional[str] = None
    quantity_to_return: float


class ReturnRequestResponse(BaseModel):
    id: int
    return_number: str
    sales_order_id: Optional[int]
    shipment_id: Optional[int]
    invoice_id: Optional[int]
    customer_id: int
    product_id: int
    request_date: date
    return_reason: str
    reason_description: Optional[str]
    quantity_to_return: float
    quantity_received: float
    status: str
    approved_by_id: Optional[int]
    approval_date: Optional[datetime]
    approval_notes: Optional[str]
    collection_date: Optional[date]
    collection_address: Optional[str]
    inspected_by_id: Optional[int]
    inspection_date: Optional[datetime]
    inspection_notes: Optional[str]
    condition_on_return: Optional[str]
    refund_amount: int
    refund_processed: int
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 88: Import/Export Documentation
# ============================================================================

class CustomsDocumentCreate(BaseModel):
    shipment_id: Optional[int] = None
    logistics_request_id: Optional[int] = None
    document_type: str  # commercial_invoice, packing_list, bill_of_lading, etc.
    document_date: date
    export_country: Optional[str] = None
    import_country: Optional[str] = None
    incoterm: Optional[str] = None
    hs_code: Optional[str] = None
    cargo_description: str
    cargo_value: int = 0  # in cents
    currency: str = "USD"


class CustomsDocumentResponse(BaseModel):
    id: int
    document_number: str
    shipment_id: Optional[int]
    logistics_request_id: Optional[int]
    document_type: str
    document_date: date
    export_country: Optional[str]
    import_country: Optional[str]
    incoterm: Optional[str]
    hs_code: Optional[str]
    cargo_description: str
    cargo_value: int
    currency: str
    status: str
    customs_reference: Optional[str]
    customs_authority: Optional[str]
    submission_date: Optional[date]
    clearance_date: Optional[date]
    document_file: Optional[str]
    supporting_documents: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 89: 3PL Integration
# ============================================================================

class ThirdPartyLogisticsCreate(BaseModel):
    provider_name: str
    provider_code: str
    provider_type: Optional[str] = None
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    integration_method: Optional[str] = None
    sync_frequency_minutes: int = 60
    contact_person: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class ThirdPartyLogisticsResponse(BaseModel):
    id: int
    provider_name: str
    provider_code: str
    provider_type: Optional[str]
    api_endpoint: Optional[str]
    integration_method: Optional[str]
    status: str
    is_active: int
    last_sync_timestamp: Optional[datetime]
    last_sync_status: Optional[str]
    sync_frequency_minutes: int
    field_mapping: Optional[str]
    sync_configuration: Optional[str]
    contact_person: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 90: Cold Chain Monitoring
# ============================================================================

class ColdChainMonitoringCreate(BaseModel):
    shipment_id: int
    sensor_id: str
    temperature_celsius: float
    min_temperature_celsius: float
    max_temperature_celsius: float
    humidity_percent: Optional[float] = None
    location: Optional[str] = None


class ColdChainMonitoringResponse(BaseModel):
    id: int
    monitoring_number: str
    shipment_id: int
    sensor_id: str
    timestamp: datetime
    temperature_celsius: float
    min_temperature_celsius: float
    max_temperature_celsius: float
    humidity_percent: Optional[float]
    location: Optional[str]
    temperature_status: str
    is_alert: int
    alert_message: Optional[str]
    corrective_action: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
