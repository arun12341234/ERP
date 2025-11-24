"""
Supply Chain & Logistics router - Processes 76-90.

This module handles:
- Logistics Request Creation
- Loading Plan Optimization
- Shipment Dispatch
- Real-Time Tracking
- Delivery Confirmation
- Freight Invoice Reconciliation
- Demand Forecasting
- Route Optimization
- Carrier Performance Review
- Warehouse Slotting
- Packaging Request
- Returns & Reverse Logistics
- Import/Export Documentation
- 3PL Integration
- Cold Chain Monitoring
"""
from datetime import datetime, date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.core.database import get_db
from app.core.config import settings
from app.models.logistics_request import LogisticsRequest, LogisticsRequestStatus
from app.models.loading_plan import LoadingPlan, LoadingPlanStatus
from app.models.shipment import Shipment, ShipmentStatus
from app.models.shipment_tracking import ShipmentTracking
from app.models.delivery_confirmation import DeliveryConfirmation
from app.models.freight_invoice import FreightInvoice, FreightInvoiceStatus
from app.models.demand_forecast import DemandForecast, DemandForecastStatus
from app.models.route_optimization import RouteOptimization, RouteOptimizationStatus
from app.models.carrier_performance import CarrierPerformance, CarrierPerformanceStatus
from app.models.warehouse_slot import WarehouseSlot
from app.models.packaging_request import PackagingRequest, PackagingRequestStatus
from app.models.return_request import ReturnRequest, ReturnRequestStatus
from app.models.customs_document import CustomsDocument, CustomsDocumentStatus
from app.models.third_party_logistics import ThirdPartyLogistics, ThirdPartyLogisticsStatus
from app.models.cold_chain_monitoring import ColdChainMonitoring, TemperatureStatus
from app.models.audit_log import AuditLog

from app.schemas.logistics import (
    LogisticsRequestCreate, LogisticsRequestResponse,
    LoadingPlanCreate, LoadingPlanResponse,
    ShipmentCreate, ShipmentResponse,
    ShipmentTrackingCreate, ShipmentTrackingResponse,
    DeliveryConfirmationCreate, DeliveryConfirmationResponse,
    FreightInvoiceCreate, FreightInvoiceResponse,
    DemandForecastCreate, DemandForecastResponse,
    RouteOptimizationCreate, RouteOptimizationResponse,
    CarrierPerformanceCreate, CarrierPerformanceResponse,
    WarehouseSlotCreate, WarehouseSlotResponse,
    PackagingRequestCreate, PackagingRequestResponse,
    ReturnRequestCreate, ReturnRequestResponse,
    CustomsDocumentCreate, CustomsDocumentResponse,
    ThirdPartyLogisticsCreate, ThirdPartyLogisticsResponse,
    ColdChainMonitoringCreate, ColdChainMonitoringResponse,
)

router = APIRouter(prefix="/logistics", tags=["logistics"])


# ============================================================================
# Helper Functions
# ============================================================================

def generate_document_number(prefix: str, db: Session) -> str:
    """Generate unique document number with format PREFIX-YYYY-NNNNN."""
    year = datetime.utcnow().year
    # This is a simple counter; in production, use a sequence or atomic counter
    count = db.query(func.count()).filter(
        func.extract('year', LogisticsRequest.created_at) == year
    ).scalar() or 0
    return f"{prefix}-{year}-{count + 1:05d}"


def apply_tenant_filter(query, model, tenant_id: Optional[int] = None):
    """Apply tenant filter if multi-tenancy is enabled."""
    if settings.ENABLE_TENANCY and tenant_id is not None:
        return query.filter(model.tenant_id == tenant_id)
    return query


def create_audit_log(db: Session, entity_type: str, entity_id: int, action: str, user_id: Optional[int] = None):
    """Create audit log entry."""
    log = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        performed_by_id=user_id,
    )
    db.add(log)
    db.commit()


# ============================================================================
# Process 76: Logistics Request Creation
# ============================================================================

@router.post("/requests", response_model=LogisticsRequestResponse, status_code=201)
def create_logistics_request(
    request: LogisticsRequestCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a new logistics request for shipment."""
    db_request = LogisticsRequest(
        request_number=generate_document_number("LGR", db),
        **request.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_request.tenant_id = tenant_id

    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    create_audit_log(db, "logistics_request", db_request.id, "created")

    return db_request


@router.get("/requests", response_model=List[LogisticsRequestResponse])
def list_logistics_requests(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    transport_mode: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List all logistics requests with filters."""
    query = db.query(LogisticsRequest)
    query = apply_tenant_filter(query, LogisticsRequest, tenant_id)

    if status:
        query = query.filter(LogisticsRequest.status == status)
    if transport_mode:
        query = query.filter(LogisticsRequest.transport_mode == transport_mode)

    return query.offset(skip).limit(limit).all()


@router.put("/requests/{request_id}/approve", response_model=LogisticsRequestResponse)
def approve_logistics_request(
    request_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Approve a logistics request."""
    db_request = db.query(LogisticsRequest).filter(LogisticsRequest.id == request_id).first()
    if not db_request:
        raise HTTPException(status_code=404, detail="Logistics request not found")

    db_request.status = LogisticsRequestStatus.APPROVED
    db_request.approved_by_id = user_id
    db_request.approval_date = datetime.utcnow()

    db.commit()
    db.refresh(db_request)

    create_audit_log(db, "logistics_request", db_request.id, "approved", user_id)

    return db_request


# ============================================================================
# Process 77: Loading Plan Optimization
# ============================================================================

@router.post("/loading-plans", response_model=LoadingPlanResponse, status_code=201)
def create_loading_plan(
    plan: LoadingPlanCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a loading plan with capacity optimization."""
    db_plan = LoadingPlan(
        plan_number=generate_document_number("LDP", db),
        **plan.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_plan.tenant_id = tenant_id

    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)

    create_audit_log(db, "loading_plan", db_plan.id, "created")

    return db_plan


@router.put("/loading-plans/{plan_id}/optimize", response_model=LoadingPlanResponse)
def optimize_loading_plan(
    plan_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Run optimization algorithm on loading plan."""
    db_plan = db.query(LoadingPlan).filter(LoadingPlan.id == plan_id).first()
    if not db_plan:
        raise HTTPException(status_code=404, detail="Loading plan not found")

    # Simple capacity utilization calculation
    if db_plan.max_capacity_kg > 0:
        db_plan.capacity_utilization_percent = (db_plan.planned_weight_kg / db_plan.max_capacity_kg) * 100

    db_plan.status = LoadingPlanStatus.OPTIMIZED
    db_plan.optimized_by_id = user_id
    db_plan.optimization_date = datetime.utcnow()

    db.commit()
    db.refresh(db_plan)

    create_audit_log(db, "loading_plan", db_plan.id, "optimized", user_id)

    return db_plan


@router.get("/loading-plans", response_model=List[LoadingPlanResponse])
def list_loading_plans(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List all loading plans."""
    query = db.query(LoadingPlan)
    query = apply_tenant_filter(query, LoadingPlan, tenant_id)

    if status:
        query = query.filter(LoadingPlan.status == status)

    return query.offset(skip).limit(limit).all()


# ============================================================================
# Process 78: Shipment Dispatch
# ============================================================================

@router.post("/shipments", response_model=ShipmentResponse, status_code=201)
def create_shipment(
    shipment: ShipmentCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a new shipment dispatch."""
    db_shipment = Shipment(
        shipment_number=generate_document_number("SHP", db),
        tracking_number=f"TRK-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        **shipment.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_shipment.tenant_id = tenant_id

    db.add(db_shipment)
    db.commit()
    db.refresh(db_shipment)

    create_audit_log(db, "shipment", db_shipment.id, "created")

    return db_shipment


@router.put("/shipments/{shipment_id}/dispatch", response_model=ShipmentResponse)
def dispatch_shipment(
    shipment_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Dispatch a shipment and mark it in transit."""
    db_shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not db_shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    db_shipment.status = ShipmentStatus.DISPATCHED
    db_shipment.dispatched_by_id = user_id

    db.commit()
    db.refresh(db_shipment)

    create_audit_log(db, "shipment", db_shipment.id, "dispatched", user_id)

    return db_shipment


@router.get("/shipments", response_model=List[ShipmentResponse])
def list_shipments(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    carrier_name: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List all shipments with filters."""
    query = db.query(Shipment)
    query = apply_tenant_filter(query, Shipment, tenant_id)

    if status:
        query = query.filter(Shipment.status == status)
    if carrier_name:
        query = query.filter(Shipment.carrier_name.ilike(f"%{carrier_name}%"))

    return query.offset(skip).limit(limit).all()


@router.get("/shipments/{shipment_id}", response_model=ShipmentResponse)
def get_shipment(shipment_id: int, db: Session = Depends(get_db)):
    """Get shipment details by ID."""
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


# ============================================================================
# Process 79: Real-Time Tracking
# ============================================================================

@router.post("/tracking", response_model=ShipmentTrackingResponse, status_code=201)
def create_tracking_update(
    tracking: ShipmentTrackingCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Add a tracking update for a shipment."""
    db_tracking = ShipmentTracking(
        tracking_timestamp=datetime.utcnow(),
        **tracking.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_tracking.tenant_id = tenant_id

    db.add(db_tracking)
    db.commit()
    db.refresh(db_tracking)

    return db_tracking


@router.get("/tracking/shipment/{shipment_id}", response_model=List[ShipmentTrackingResponse])
def get_shipment_tracking(shipment_id: int, db: Session = Depends(get_db)):
    """Get all tracking updates for a shipment."""
    tracking = db.query(ShipmentTracking).filter(
        ShipmentTracking.shipment_id == shipment_id
    ).order_by(ShipmentTracking.tracking_timestamp.desc()).all()

    return tracking


# ============================================================================
# Process 80: Delivery Confirmation
# ============================================================================

@router.post("/delivery-confirmations", response_model=DeliveryConfirmationResponse, status_code=201)
def create_delivery_confirmation(
    confirmation: DeliveryConfirmationCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create proof of delivery."""
    db_confirmation = DeliveryConfirmation(
        confirmation_number=generate_document_number("POD", db),
        delivery_date=date.today(),
        delivery_time=datetime.utcnow(),
        **confirmation.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_confirmation.tenant_id = tenant_id

    db.add(db_confirmation)
    db.commit()
    db.refresh(db_confirmation)

    # Update shipment status to delivered
    shipment = db.query(Shipment).filter(Shipment.id == confirmation.shipment_id).first()
    if shipment:
        shipment.status = ShipmentStatus.DELIVERED
        shipment.actual_delivery_date = date.today()
        db.commit()

    create_audit_log(db, "delivery_confirmation", db_confirmation.id, "created")

    return db_confirmation


@router.put("/delivery-confirmations/{confirmation_id}/confirm", response_model=DeliveryConfirmationResponse)
def confirm_delivery(
    confirmation_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Confirm a delivery."""
    db_confirmation = db.query(DeliveryConfirmation).filter(
        DeliveryConfirmation.id == confirmation_id
    ).first()
    if not db_confirmation:
        raise HTTPException(status_code=404, detail="Delivery confirmation not found")

    db_confirmation.is_confirmed = 1
    db_confirmation.confirmed_by_id = user_id

    db.commit()
    db.refresh(db_confirmation)

    create_audit_log(db, "delivery_confirmation", db_confirmation.id, "confirmed", user_id)

    return db_confirmation


@router.get("/delivery-confirmations", response_model=List[DeliveryConfirmationResponse])
def list_delivery_confirmations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List all delivery confirmations."""
    query = db.query(DeliveryConfirmation)
    query = apply_tenant_filter(query, DeliveryConfirmation, tenant_id)

    return query.offset(skip).limit(limit).all()


# ============================================================================
# Process 81: Freight Invoice Reconciliation
# ============================================================================

@router.post("/freight-invoices", response_model=FreightInvoiceResponse, status_code=201)
def create_freight_invoice(
    invoice: FreightInvoiceCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a freight invoice."""
    total_amount = (
        invoice.freight_charges +
        invoice.fuel_surcharge +
        invoice.handling_charges +
        invoice.other_charges
    )

    db_invoice = FreightInvoice(
        invoice_number=generate_document_number("FRT", db),
        total_amount=total_amount,
        **invoice.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_invoice.tenant_id = tenant_id

    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)

    create_audit_log(db, "freight_invoice", db_invoice.id, "created")

    return db_invoice


@router.put("/freight-invoices/{invoice_id}/verify", response_model=FreightInvoiceResponse)
def verify_freight_invoice(
    invoice_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Verify a freight invoice against shipment costs."""
    db_invoice = db.query(FreightInvoice).filter(FreightInvoice.id == invoice_id).first()
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Freight invoice not found")

    # Get logistics request to compare costs
    shipment = db.query(Shipment).filter(Shipment.id == db_invoice.shipment_id).first()
    if shipment:
        request = db.query(LogisticsRequest).filter(
            LogisticsRequest.id == shipment.logistics_request_id
        ).first()
        if request:
            db_invoice.variance_amount = db_invoice.total_amount - request.estimated_cost

    db_invoice.status = FreightInvoiceStatus.VERIFIED
    db_invoice.verified_by_id = user_id
    db_invoice.verification_date = datetime.utcnow()

    db.commit()
    db.refresh(db_invoice)

    create_audit_log(db, "freight_invoice", db_invoice.id, "verified", user_id)

    return db_invoice


@router.get("/freight-invoices", response_model=List[FreightInvoiceResponse])
def list_freight_invoices(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List all freight invoices."""
    query = db.query(FreightInvoice)
    query = apply_tenant_filter(query, FreightInvoice, tenant_id)

    if status:
        query = query.filter(FreightInvoice.status == status)

    return query.offset(skip).limit(limit).all()


# ============================================================================
# Process 82: Demand Forecasting
# ============================================================================

@router.post("/demand-forecasts", response_model=DemandForecastResponse, status_code=201)
def create_demand_forecast(
    forecast: DemandForecastCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a demand forecast."""
    db_forecast = DemandForecast(
        forecast_number=generate_document_number("DFC", db),
        **forecast.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_forecast.tenant_id = tenant_id

    db.add(db_forecast)
    db.commit()
    db.refresh(db_forecast)

    create_audit_log(db, "demand_forecast", db_forecast.id, "created")

    return db_forecast


@router.put("/demand-forecasts/{forecast_id}/approve", response_model=DemandForecastResponse)
def approve_demand_forecast(
    forecast_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Approve a demand forecast."""
    db_forecast = db.query(DemandForecast).filter(DemandForecast.id == forecast_id).first()
    if not db_forecast:
        raise HTTPException(status_code=404, detail="Demand forecast not found")

    db_forecast.status = DemandForecastStatus.APPROVED
    db_forecast.approved_by_id = user_id
    db_forecast.approval_date = datetime.utcnow()

    db.commit()
    db.refresh(db_forecast)

    create_audit_log(db, "demand_forecast", db_forecast.id, "approved", user_id)

    return db_forecast


@router.get("/demand-forecasts", response_model=List[DemandForecastResponse])
def list_demand_forecasts(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List all demand forecasts."""
    query = db.query(DemandForecast)
    query = apply_tenant_filter(query, DemandForecast, tenant_id)

    if product_id:
        query = query.filter(DemandForecast.product_id == product_id)

    return query.offset(skip).limit(limit).all()


# ============================================================================
# Process 83: Route Optimization
# ============================================================================

@router.post("/route-optimizations", response_model=RouteOptimizationResponse, status_code=201)
def create_route_optimization(
    route: RouteOptimizationCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a route optimization request."""
    db_route = RouteOptimization(
        route_number=generate_document_number("RTO", db),
        **route.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_route.tenant_id = tenant_id

    db.add(db_route)
    db.commit()
    db.refresh(db_route)

    create_audit_log(db, "route_optimization", db_route.id, "created")

    return db_route


@router.put("/route-optimizations/{route_id}/optimize", response_model=RouteOptimizationResponse)
def optimize_route(
    route_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Run route optimization algorithm."""
    db_route = db.query(RouteOptimization).filter(RouteOptimization.id == route_id).first()
    if not db_route:
        raise HTTPException(status_code=404, detail="Route optimization not found")

    # Simple estimation (in production, use actual routing API)
    db_route.total_distance_km = 150.0  # Placeholder
    db_route.estimated_time_hours = 3.5  # Placeholder
    db_route.estimated_cost = 15000  # $150.00

    db_route.status = RouteOptimizationStatus.OPTIMIZED
    db_route.optimized_by_id = user_id
    db_route.optimization_date = datetime.utcnow()

    db.commit()
    db.refresh(db_route)

    create_audit_log(db, "route_optimization", db_route.id, "optimized", user_id)

    return db_route


@router.get("/route-optimizations", response_model=List[RouteOptimizationResponse])
def list_route_optimizations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List all route optimizations."""
    query = db.query(RouteOptimization)
    query = apply_tenant_filter(query, RouteOptimization, tenant_id)

    return query.offset(skip).limit(limit).all()


# ============================================================================
# Process 84: Carrier Performance Review
# ============================================================================

@router.post("/carrier-performance", response_model=CarrierPerformanceResponse, status_code=201)
def create_carrier_performance(
    performance: CarrierPerformanceCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a carrier performance review."""
    # Calculate metrics
    on_time_pct = 0.0
    damage_rate = 0.0
    loss_rate = 0.0

    if performance.total_shipments > 0:
        on_time_pct = (performance.on_time_deliveries / performance.total_shipments) * 100
        damage_rate = (performance.damaged_shipments / performance.total_shipments) * 100
        loss_rate = (performance.lost_shipments / performance.total_shipments) * 100

    db_performance = CarrierPerformance(
        review_number=generate_document_number("CPR", db),
        on_time_percentage=on_time_pct,
        damage_rate_percentage=damage_rate,
        loss_rate_percentage=loss_rate,
        **performance.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_performance.tenant_id = tenant_id

    db.add(db_performance)
    db.commit()
    db.refresh(db_performance)

    create_audit_log(db, "carrier_performance", db_performance.id, "created")

    return db_performance


@router.get("/carrier-performance", response_model=List[CarrierPerformanceResponse])
def list_carrier_performance(
    skip: int = 0,
    limit: int = 100,
    carrier_name: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List carrier performance reviews."""
    query = db.query(CarrierPerformance)
    query = apply_tenant_filter(query, CarrierPerformance, tenant_id)

    if carrier_name:
        query = query.filter(CarrierPerformance.carrier_name.ilike(f"%{carrier_name}%"))

    return query.offset(skip).limit(limit).all()


# ============================================================================
# Process 85: Warehouse Slotting
# ============================================================================

@router.post("/warehouse-slots", response_model=WarehouseSlotResponse, status_code=201)
def create_warehouse_slot(
    slot: WarehouseSlotCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a warehouse slot."""
    slot_code = f"{slot.warehouse_location}-{slot.zone}-{slot.aisle}-{slot.rack}-{slot.shelf}-{slot.bin}"

    db_slot = WarehouseSlot(
        slot_code=slot_code,
        **slot.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_slot.tenant_id = tenant_id

    db.add(db_slot)
    db.commit()
    db.refresh(db_slot)

    create_audit_log(db, "warehouse_slot", db_slot.id, "created")

    return db_slot


@router.get("/warehouse-slots", response_model=List[WarehouseSlotResponse])
def list_warehouse_slots(
    skip: int = 0,
    limit: int = 100,
    warehouse_location: Optional[str] = None,
    is_available: Optional[bool] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List warehouse slots with availability."""
    query = db.query(WarehouseSlot)
    query = apply_tenant_filter(query, WarehouseSlot, tenant_id)

    if warehouse_location:
        query = query.filter(WarehouseSlot.warehouse_location == warehouse_location)
    if is_available is not None:
        query = query.filter(WarehouseSlot.is_available == (1 if is_available else 0))

    return query.offset(skip).limit(limit).all()


# ============================================================================
# Process 86: Packaging Request
# ============================================================================

@router.post("/packaging-requests", response_model=PackagingRequestResponse, status_code=201)
def create_packaging_request(
    request: PackagingRequestCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a packaging request."""
    db_request = PackagingRequest(
        request_number=generate_document_number("PKG", db),
        **request.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_request.tenant_id = tenant_id

    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    create_audit_log(db, "packaging_request", db_request.id, "created")

    return db_request


@router.put("/packaging-requests/{request_id}/pack", response_model=PackagingRequestResponse)
def complete_packaging(
    request_id: int,
    quantity_packed: float,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Complete packaging request."""
    db_request = db.query(PackagingRequest).filter(PackagingRequest.id == request_id).first()
    if not db_request:
        raise HTTPException(status_code=404, detail="Packaging request not found")

    db_request.quantity_packed = quantity_packed
    db_request.status = PackagingRequestStatus.PACKED if quantity_packed >= db_request.quantity_to_pack else PackagingRequestStatus.IN_PROGRESS
    db_request.packed_by_id = user_id
    db_request.packed_date = datetime.utcnow()

    db.commit()
    db.refresh(db_request)

    create_audit_log(db, "packaging_request", db_request.id, "packed", user_id)

    return db_request


@router.get("/packaging-requests", response_model=List[PackagingRequestResponse])
def list_packaging_requests(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List packaging requests."""
    query = db.query(PackagingRequest)
    query = apply_tenant_filter(query, PackagingRequest, tenant_id)

    if status:
        query = query.filter(PackagingRequest.status == status)

    return query.offset(skip).limit(limit).all()


# ============================================================================
# Process 87: Returns & Reverse Logistics
# ============================================================================

@router.post("/return-requests", response_model=ReturnRequestResponse, status_code=201)
def create_return_request(
    request: ReturnRequestCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a return request."""
    db_request = ReturnRequest(
        return_number=generate_document_number("RET", db),
        **request.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_request.tenant_id = tenant_id

    db.add(db_request)
    db.commit()
    db.refresh(db_request)

    create_audit_log(db, "return_request", db_request.id, "created")

    return db_request


@router.put("/return-requests/{request_id}/approve", response_model=ReturnRequestResponse)
def approve_return_request(
    request_id: int,
    user_id: int,
    approval_notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Approve a return request."""
    db_request = db.query(ReturnRequest).filter(ReturnRequest.id == request_id).first()
    if not db_request:
        raise HTTPException(status_code=404, detail="Return request not found")

    db_request.status = ReturnRequestStatus.APPROVED
    db_request.approved_by_id = user_id
    db_request.approval_date = datetime.utcnow()
    db_request.approval_notes = approval_notes

    db.commit()
    db.refresh(db_request)

    create_audit_log(db, "return_request", db_request.id, "approved", user_id)

    return db_request


@router.put("/return-requests/{request_id}/inspect", response_model=ReturnRequestResponse)
def inspect_returned_item(
    request_id: int,
    user_id: int,
    condition_on_return: str,
    inspection_notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Inspect returned item."""
    db_request = db.query(ReturnRequest).filter(ReturnRequest.id == request_id).first()
    if not db_request:
        raise HTTPException(status_code=404, detail="Return request not found")

    db_request.status = ReturnRequestStatus.INSPECTED
    db_request.inspected_by_id = user_id
    db_request.inspection_date = datetime.utcnow()
    db_request.condition_on_return = condition_on_return
    db_request.inspection_notes = inspection_notes

    db.commit()
    db.refresh(db_request)

    create_audit_log(db, "return_request", db_request.id, "inspected", user_id)

    return db_request


@router.get("/return-requests", response_model=List[ReturnRequestResponse])
def list_return_requests(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List return requests."""
    query = db.query(ReturnRequest)
    query = apply_tenant_filter(query, ReturnRequest, tenant_id)

    if status:
        query = query.filter(ReturnRequest.status == status)

    return query.offset(skip).limit(limit).all()


# ============================================================================
# Process 88: Import/Export Documentation
# ============================================================================

@router.post("/customs-documents", response_model=CustomsDocumentResponse, status_code=201)
def create_customs_document(
    document: CustomsDocumentCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a customs document."""
    db_document = CustomsDocument(
        document_number=generate_document_number("CUS", db),
        **document.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_document.tenant_id = tenant_id

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    create_audit_log(db, "customs_document", db_document.id, "created")

    return db_document


@router.put("/customs-documents/{document_id}/submit", response_model=CustomsDocumentResponse)
def submit_customs_document(
    document_id: int,
    submission_date: date,
    customs_reference: str,
    db: Session = Depends(get_db)
):
    """Submit customs document to authorities."""
    db_document = db.query(CustomsDocument).filter(CustomsDocument.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Customs document not found")

    db_document.status = CustomsDocumentStatus.SUBMITTED
    db_document.submission_date = submission_date
    db_document.customs_reference = customs_reference

    db.commit()
    db.refresh(db_document)

    create_audit_log(db, "customs_document", db_document.id, "submitted")

    return db_document


@router.get("/customs-documents", response_model=List[CustomsDocumentResponse])
def list_customs_documents(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    document_type: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List customs documents."""
    query = db.query(CustomsDocument)
    query = apply_tenant_filter(query, CustomsDocument, tenant_id)

    if status:
        query = query.filter(CustomsDocument.status == status)
    if document_type:
        query = query.filter(CustomsDocument.document_type == document_type)

    return query.offset(skip).limit(limit).all()


# ============================================================================
# Process 89: 3PL Integration
# ============================================================================

@router.post("/3pl-providers", response_model=ThirdPartyLogisticsResponse, status_code=201)
def create_3pl_provider(
    provider: ThirdPartyLogisticsCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Register a 3PL provider."""
    db_provider = ThirdPartyLogistics(
        **provider.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_provider.tenant_id = tenant_id

    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)

    create_audit_log(db, "third_party_logistics", db_provider.id, "created")

    return db_provider


@router.put("/3pl-providers/{provider_id}/sync", response_model=ThirdPartyLogisticsResponse)
def sync_3pl_provider(
    provider_id: int,
    db: Session = Depends(get_db)
):
    """Synchronize data with 3PL provider."""
    db_provider = db.query(ThirdPartyLogistics).filter(ThirdPartyLogistics.id == provider_id).first()
    if not db_provider:
        raise HTTPException(status_code=404, detail="3PL provider not found")

    db_provider.status = ThirdPartyLogisticsStatus.SYNCING
    db_provider.last_sync_timestamp = datetime.utcnow()
    db_provider.last_sync_status = "success"

    # In production, this would call the actual 3PL API

    db_provider.status = ThirdPartyLogisticsStatus.ACTIVE

    db.commit()
    db.refresh(db_provider)

    create_audit_log(db, "third_party_logistics", db_provider.id, "synced")

    return db_provider


@router.get("/3pl-providers", response_model=List[ThirdPartyLogisticsResponse])
def list_3pl_providers(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List 3PL providers."""
    query = db.query(ThirdPartyLogistics)
    query = apply_tenant_filter(query, ThirdPartyLogistics, tenant_id)

    if status:
        query = query.filter(ThirdPartyLogistics.status == status)

    return query.offset(skip).limit(limit).all()


# ============================================================================
# Process 90: Cold Chain Monitoring
# ============================================================================

@router.post("/cold-chain", response_model=ColdChainMonitoringResponse, status_code=201)
def create_cold_chain_monitoring(
    monitoring: ColdChainMonitoringCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a cold chain monitoring record."""
    # Check temperature thresholds
    temp_status = TemperatureStatus.NORMAL
    is_alert = 0
    alert_message = None

    if monitoring.temperature_celsius < monitoring.min_temperature_celsius:
        temp_status = TemperatureStatus.CRITICAL
        is_alert = 1
        alert_message = f"Temperature {monitoring.temperature_celsius}°C below minimum {monitoring.min_temperature_celsius}°C"
    elif monitoring.temperature_celsius > monitoring.max_temperature_celsius:
        temp_status = TemperatureStatus.CRITICAL
        is_alert = 1
        alert_message = f"Temperature {monitoring.temperature_celsius}°C above maximum {monitoring.max_temperature_celsius}°C"
    elif monitoring.temperature_celsius < (monitoring.min_temperature_celsius + 2):
        temp_status = TemperatureStatus.WARNING
        alert_message = f"Temperature {monitoring.temperature_celsius}°C approaching minimum threshold"
    elif monitoring.temperature_celsius > (monitoring.max_temperature_celsius - 2):
        temp_status = TemperatureStatus.WARNING
        alert_message = f"Temperature {monitoring.temperature_celsius}°C approaching maximum threshold"

    db_monitoring = ColdChainMonitoring(
        monitoring_number=generate_document_number("CCM", db),
        timestamp=datetime.utcnow(),
        temperature_status=temp_status,
        is_alert=is_alert,
        alert_message=alert_message,
        **monitoring.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_monitoring.tenant_id = tenant_id

    db.add(db_monitoring)
    db.commit()
    db.refresh(db_monitoring)

    if is_alert:
        create_audit_log(db, "cold_chain_monitoring", db_monitoring.id, "alert_created")

    return db_monitoring


@router.get("/cold-chain/shipment/{shipment_id}", response_model=List[ColdChainMonitoringResponse])
def get_cold_chain_monitoring(
    shipment_id: int,
    db: Session = Depends(get_db)
):
    """Get cold chain monitoring data for a shipment."""
    monitoring = db.query(ColdChainMonitoring).filter(
        ColdChainMonitoring.shipment_id == shipment_id
    ).order_by(ColdChainMonitoring.timestamp.desc()).all()

    return monitoring


@router.get("/cold-chain/alerts", response_model=List[ColdChainMonitoringResponse])
def get_cold_chain_alerts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Get all cold chain alerts."""
    query = db.query(ColdChainMonitoring)
    query = apply_tenant_filter(query, ColdChainMonitoring, tenant_id)
    query = query.filter(ColdChainMonitoring.is_alert == 1)

    return query.order_by(ColdChainMonitoring.timestamp.desc()).offset(skip).limit(limit).all()
