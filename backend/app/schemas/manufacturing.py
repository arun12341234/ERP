"""
Manufacturing schemas for request/response validation.
"""
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel


# Production Plan schemas
class ProductionPlanCreate(BaseModel):
    plan_date: date
    start_date: date
    end_date: date
    total_capacity_hours: float = 0.0
    notes: Optional[str] = None


class ProductionPlanResponse(BaseModel):
    id: int
    plan_number: str
    plan_date: date
    start_date: date
    end_date: date
    total_capacity_hours: float
    allocated_hours: float
    utilization_percent: float
    status: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Work Order schemas
class WorkOrderCreate(BaseModel):
    product_id: int
    production_plan_id: Optional[int] = None
    quantity_planned: float
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    priority: int = 5
    notes: Optional[str] = None


class WorkOrderResponse(BaseModel):
    id: int
    wo_number: str
    product_id: int
    production_plan_id: Optional[int]
    quantity_planned: float
    quantity_produced: float
    quantity_scrapped: float
    scheduled_start: Optional[datetime]
    scheduled_end: Optional[datetime]
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    priority: int
    status: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Material Issue schemas
class MaterialIssueCreate(BaseModel):
    work_order_id: int
    product_id: int
    location_id: Optional[int] = None
    quantity_requested: float
    notes: Optional[str] = None


class MaterialIssueResponse(BaseModel):
    id: int
    issue_number: str
    work_order_id: int
    product_id: int
    location_id: Optional[int]
    quantity_requested: float
    quantity_issued: float
    quantity_returned: float
    unit_cost: float
    total_cost: float
    status: str
    issued_by_id: Optional[int]
    issued_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Machine schemas
class MachineCreate(BaseModel):
    machine_code: str
    name: str
    machine_type: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    hourly_capacity: float = 0.0
    daily_capacity_hours: float = 8.0
    department: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None


class MachineResponse(BaseModel):
    id: int
    machine_code: str
    name: str
    machine_type: Optional[str]
    manufacturer: Optional[str]
    model: Optional[str]
    hourly_capacity: float
    daily_capacity_hours: float
    status: str
    is_active: bool
    department: Optional[str]
    location: Optional[str]
    last_maintenance_date: Optional[datetime]
    next_maintenance_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Machine Schedule schemas
class MachineScheduleCreate(BaseModel):
    machine_id: int
    work_order_id: int
    scheduled_start: datetime
    scheduled_end: datetime
    planned_hours: float


class MachineScheduleResponse(BaseModel):
    id: int
    machine_id: int
    work_order_id: int
    scheduled_start: datetime
    scheduled_end: datetime
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    planned_hours: float
    actual_hours: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# Labor Allocation schemas
class LaborAllocationCreate(BaseModel):
    worker_id: int
    work_order_id: int
    role: Optional[str] = None
    skill_level: Optional[str] = None
    scheduled_start: datetime
    scheduled_end: datetime
    planned_hours: float


class LaborAllocationResponse(BaseModel):
    id: int
    worker_id: int
    work_order_id: int
    role: Optional[str]
    skill_level: Optional[str]
    scheduled_start: datetime
    scheduled_end: datetime
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    planned_hours: float
    actual_hours: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# Shopfloor Job schemas
class ShopfloorJobCreate(BaseModel):
    work_order_id: int
    worker_id: int
    machine_id: Optional[int] = None
    operation_name: str
    operation_sequence: int = 1
    quantity_assigned: float
    assigned_at: datetime
    notes: Optional[str] = None


class ShopfloorJobResponse(BaseModel):
    id: int
    job_number: str
    work_order_id: int
    worker_id: int
    machine_id: Optional[int]
    operation_name: str
    operation_sequence: int
    quantity_assigned: float
    quantity_completed: float
    assigned_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    status: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Production Execution schemas
class ProductionExecutionCreate(BaseModel):
    work_order_id: int
    job_id: Optional[int] = None
    quantity_produced: float
    quantity_good: float = 0.0
    quantity_rejected: float = 0.0
    execution_date: datetime
    duration_hours: float = 0.0
    operator_id: Optional[int] = None
    machine_id: Optional[int] = None
    notes: Optional[str] = None


class ProductionExecutionResponse(BaseModel):
    id: int
    work_order_id: int
    job_id: Optional[int]
    quantity_produced: float
    quantity_good: float
    quantity_rejected: float
    execution_date: datetime
    duration_hours: float
    operator_id: Optional[int]
    machine_id: Optional[int]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Downtime schemas
class DowntimeCreate(BaseModel):
    machine_id: int
    work_order_id: Optional[int] = None
    downtime_type: str
    reason: Optional[str] = None
    description: Optional[str] = None
    start_time: datetime
    reported_by_id: Optional[int] = None


class DowntimeResponse(BaseModel):
    id: int
    machine_id: int
    work_order_id: Optional[int]
    downtime_type: str
    reason: Optional[str]
    description: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    duration_hours: float
    reported_by_id: Optional[int]
    resolution: Optional[str]
    resolved_by_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# Quality Check Production schemas
class QualityCheckProductionCreate(BaseModel):
    work_order_id: int
    execution_id: Optional[int] = None
    check_type: str
    check_point: Optional[str] = None
    sample_size: float
    inspection_date: datetime
    inspector_id: Optional[int] = None
    notes: Optional[str] = None


class QualityCheckProductionResponse(BaseModel):
    id: int
    check_number: str
    work_order_id: int
    execution_id: Optional[int]
    check_type: str
    check_point: Optional[str]
    sample_size: float
    quantity_passed: float
    quantity_failed: float
    result: str
    defects_found: Optional[str]
    inspector_id: Optional[int]
    inspection_date: datetime
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Rework Order schemas
class ReworkOrderCreate(BaseModel):
    work_order_id: int
    quality_check_id: Optional[int] = None
    product_id: int
    quantity_to_rework: float
    defect_description: str
    rework_instructions: Optional[str] = None
    estimated_cost: float = 0.0
    assigned_to_id: Optional[int] = None
    notes: Optional[str] = None


class ReworkOrderResponse(BaseModel):
    id: int
    rework_number: str
    work_order_id: int
    quality_check_id: Optional[int]
    product_id: int
    quantity_to_rework: float
    quantity_completed: float
    quantity_scrapped: float
    defect_description: str
    rework_instructions: Optional[str]
    status: str
    estimated_cost: float
    actual_cost: float
    assigned_to_id: Optional[int]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Scrap Record schemas
class ScrapRecordCreate(BaseModel):
    work_order_id: Optional[int] = None
    product_id: int
    quantity_scrapped: float
    scrap_reason: str
    description: Optional[str] = None
    unit_cost: float = 0.0
    scrap_date: datetime
    recorded_by_id: Optional[int] = None
    disposal_method: Optional[str] = None
    notes: Optional[str] = None


class ScrapRecordResponse(BaseModel):
    id: int
    scrap_number: str
    work_order_id: Optional[int]
    product_id: int
    quantity_scrapped: float
    scrap_reason: str
    description: Optional[str]
    unit_cost: float
    total_cost: float
    recorded_by_id: Optional[int]
    scrap_date: datetime
    disposal_method: Optional[str]
    disposal_date: Optional[datetime]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Finished Goods Receipt schemas
class FinishedGoodsReceiptCreate(BaseModel):
    work_order_id: int
    product_id: int
    quantity_received: float
    location_id: Optional[int] = None
    unit_cost: float = 0.0
    notes: Optional[str] = None


class FinishedGoodsReceiptResponse(BaseModel):
    id: int
    receipt_number: str
    work_order_id: int
    product_id: int
    quantity_received: float
    location_id: Optional[int]
    status: str
    received_by_id: Optional[int]
    received_date: Optional[datetime]
    unit_cost: float
    total_cost: float
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Maintenance Request schemas
class MaintenanceRequestCreate(BaseModel):
    machine_id: int
    issue_description: str
    priority: str = "medium"
    requested_by_id: int


class MaintenanceRequestResponse(BaseModel):
    id: int
    request_number: str
    machine_id: int
    issue_description: str
    priority: str
    status: str
    requested_by_id: int
    request_date: datetime
    assigned_to_id: Optional[int]
    scheduled_date: Optional[datetime]
    completed_date: Optional[datetime]
    work_performed: Optional[str]
    resolution_notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Preventive Maintenance schemas
class PreventiveMaintenanceCreate(BaseModel):
    machine_id: int
    pm_type: str
    description: Optional[str] = None
    checklist: Optional[str] = None
    scheduled_date: datetime
    frequency_days: Optional[int] = None
    assigned_to_id: Optional[int] = None


class PreventiveMaintenanceResponse(BaseModel):
    id: int
    pm_number: str
    machine_id: int
    pm_type: str
    description: Optional[str]
    checklist: Optional[str]
    scheduled_date: datetime
    frequency_days: Optional[int]
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    duration_hours: float
    status: str
    assigned_to_id: Optional[int]
    work_performed: Optional[str]
    parts_replaced: Optional[str]
    findings: Optional[str]
    next_pm_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
