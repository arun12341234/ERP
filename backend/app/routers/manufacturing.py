"""
Manufacturing router - Production, Operations & Manufacturing (processes 31-45).
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models import (
    ProductionPlan, WorkOrder, MaterialIssue, Machine, MachineSchedule,
    LaborAllocation, ShopfloorJob, ProductionExecution, Downtime,
    QualityCheckProduction, ReworkOrder, ScrapRecord, FinishedGoodsReceipt,
    MaintenanceRequest, PreventiveMaintenance, Product, StockItem
)
from app.schemas.manufacturing import (
    ProductionPlanCreate, ProductionPlanResponse,
    WorkOrderCreate, WorkOrderResponse,
    MaterialIssueCreate, MaterialIssueResponse,
    MachineCreate, MachineResponse,
    MachineScheduleCreate, MachineScheduleResponse,
    LaborAllocationCreate, LaborAllocationResponse,
    ShopfloorJobCreate, ShopfloorJobResponse,
    ProductionExecutionCreate, ProductionExecutionResponse,
    DowntimeCreate, DowntimeResponse,
    QualityCheckProductionCreate, QualityCheckProductionResponse,
    ReworkOrderCreate, ReworkOrderResponse,
    ScrapRecordCreate, ScrapRecordResponse,
    FinishedGoodsReceiptCreate, FinishedGoodsReceiptResponse,
    MaintenanceRequestCreate, MaintenanceRequestResponse,
    PreventiveMaintenanceCreate, PreventiveMaintenanceResponse,
)

router = APIRouter(tags=["manufacturing"])


def apply_tenant_filter(query, model, tenant_id: Optional[int] = None):
    """Apply tenant filter if multi-tenancy is enabled."""
    if settings.ENABLE_TENANCY and tenant_id is not None:
        return query.filter(model.tenant_id == tenant_id)
    return query


# ============================================================================
# Process 31: Production Planning
# ============================================================================

@router.post("/production-plans", response_model=ProductionPlanResponse)
def create_production_plan(
    plan: ProductionPlanCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """
    Process 31: Production Planning
    Input: Forecast, orders → Capacity planning
    Output: Production plan
    """
    # Generate plan number
    count = db.query(ProductionPlan).count()
    plan_number = f"PLAN-{datetime.now().year}-{count + 1:05d}"

    db_plan = ProductionPlan(
        plan_number=plan_number,
        plan_date=plan.plan_date,
        start_date=plan.start_date,
        end_date=plan.end_date,
        total_capacity_hours=plan.total_capacity_hours,
        notes=plan.notes,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


@router.get("/production-plans", response_model=List[ProductionPlanResponse])
def list_production_plans(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List all production plans."""
    query = db.query(ProductionPlan)
    query = apply_tenant_filter(query, ProductionPlan, tenant_id)
    if status:
        query = query.filter(ProductionPlan.status == status)
    return query.order_by(ProductionPlan.created_at.desc()).all()


@router.post("/production-plans/{plan_id}/approve")
def approve_production_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """Approve a production plan."""
    plan = db.query(ProductionPlan).filter(ProductionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Production plan not found")

    plan.status = "approved"
    db.commit()
    return {"message": "Production plan approved", "plan_number": plan.plan_number}


# ============================================================================
# Process 32: Work Order Creation
# ============================================================================

@router.post("/work-orders", response_model=WorkOrderResponse)
def create_work_order(
    wo: WorkOrderCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """
    Process 32: Work Order Creation
    Input: Production plan → Authorize order
    Output: Work order
    """
    # Verify product exists
    product = db.query(Product).filter(Product.id == wo.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Generate WO number
    count = db.query(WorkOrder).count()
    wo_number = f"WO-{datetime.now().year}-{count + 1:05d}"

    db_wo = WorkOrder(
        wo_number=wo_number,
        product_id=wo.product_id,
        production_plan_id=wo.production_plan_id,
        quantity_planned=wo.quantity_planned,
        scheduled_start=wo.scheduled_start,
        scheduled_end=wo.scheduled_end,
        priority=wo.priority,
        notes=wo.notes,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_wo)
    db.commit()
    db.refresh(db_wo)
    return db_wo


@router.get("/work-orders", response_model=List[WorkOrderResponse])
def list_work_orders(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List all work orders."""
    query = db.query(WorkOrder)
    query = apply_tenant_filter(query, WorkOrder, tenant_id)
    if status:
        query = query.filter(WorkOrder.status == status)
    return query.order_by(WorkOrder.priority.desc(), WorkOrder.created_at.desc()).all()


@router.get("/work-orders/{wo_id}", response_model=WorkOrderResponse)
def get_work_order(
    wo_id: int,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """Get work order details."""
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")
    return wo


@router.post("/work-orders/{wo_id}/release")
def release_work_order(
    wo_id: int,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """Release a work order to production."""
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")

    wo.status = "released"
    db.commit()
    return {"message": "Work order released", "wo_number": wo.wo_number}


@router.post("/work-orders/{wo_id}/start")
def start_work_order(
    wo_id: int,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """Start work order execution."""
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")

    wo.status = "in_progress"
    wo.actual_start = datetime.utcnow()
    db.commit()
    return {"message": "Work order started", "wo_number": wo.wo_number}


# ============================================================================
# Process 33: Material Issue to Production
# ============================================================================

@router.post("/material-issues", response_model=MaterialIssueResponse)
def create_material_issue(
    issue: MaterialIssueCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """
    Process 33: Material Issue to Production
    Input: Work order, inventory → Material requisition
    Output: Material issue
    """
    # Verify work order exists
    wo = db.query(WorkOrder).filter(WorkOrder.id == issue.work_order_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")

    # Generate issue number
    count = db.query(MaterialIssue).count()
    issue_number = f"MI-{datetime.now().year}-{count + 1:05d}"

    db_issue = MaterialIssue(
        issue_number=issue_number,
        work_order_id=issue.work_order_id,
        product_id=issue.product_id,
        location_id=issue.location_id,
        quantity_requested=issue.quantity_requested,
        notes=issue.notes,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue


@router.get("/material-issues", response_model=List[MaterialIssueResponse])
def list_material_issues(
    work_order_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List material issues."""
    query = db.query(MaterialIssue)
    query = apply_tenant_filter(query, MaterialIssue, tenant_id)
    if work_order_id:
        query = query.filter(MaterialIssue.work_order_id == work_order_id)
    if status:
        query = query.filter(MaterialIssue.status == status)
    return query.order_by(MaterialIssue.created_at.desc()).all()


@router.post("/material-issues/{issue_id}/issue")
def issue_material(
    issue_id: int,
    quantity: float,
    issued_by_id: int,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """Issue materials to production."""
    issue = db.query(MaterialIssue).filter(MaterialIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Material issue not found")

    # Update stock if location is specified
    if issue.location_id:
        stock_item = db.query(StockItem).filter(
            StockItem.product_id == issue.product_id,
            StockItem.location_id == issue.location_id
        ).first()

        if stock_item:
            if stock_item.quantity < quantity:
                raise HTTPException(status_code=400, detail="Insufficient stock")

            stock_item.quantity -= quantity
            issue.unit_cost = stock_item.unit_cost

    issue.quantity_issued = quantity
    issue.total_cost = quantity * issue.unit_cost
    issue.status = "issued"
    issue.issued_by_id = issued_by_id
    issue.issued_at = datetime.utcnow()
    db.commit()
    return {"message": "Material issued", "issue_number": issue.issue_number}


# ============================================================================
# Process 34: Machine Scheduling
# ============================================================================

@router.post("/machines", response_model=MachineResponse)
def create_machine(
    machine: MachineCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """Create a machine."""
    # Check for duplicate machine code
    existing = db.query(Machine).filter(Machine.machine_code == machine.machine_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Machine code already exists")

    db_machine = Machine(
        machine_code=machine.machine_code,
        name=machine.name,
        machine_type=machine.machine_type,
        manufacturer=machine.manufacturer,
        model=machine.model,
        hourly_capacity=machine.hourly_capacity,
        daily_capacity_hours=machine.daily_capacity_hours,
        department=machine.department,
        location=machine.location,
        notes=machine.notes,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)
    return db_machine


@router.get("/machines", response_model=List[MachineResponse])
def list_machines(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List all machines."""
    query = db.query(Machine)
    query = apply_tenant_filter(query, Machine, tenant_id)
    if status:
        query = query.filter(Machine.status == status)
    return query.order_by(Machine.machine_code).all()


@router.post("/machine-schedules", response_model=MachineScheduleResponse)
def create_machine_schedule(
    schedule: MachineScheduleCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """
    Process 34: Machine Scheduling
    Input: Work orders → Schedule optimization
    Output: Machine schedule
    """
    # Verify machine exists
    machine = db.query(Machine).filter(Machine.id == schedule.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    # Verify work order exists
    wo = db.query(WorkOrder).filter(WorkOrder.id == schedule.work_order_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")

    # Check for scheduling conflicts (simplified)
    conflict = db.query(MachineSchedule).filter(
        MachineSchedule.machine_id == schedule.machine_id,
        MachineSchedule.status.in_(["planned", "confirmed", "in_progress"]),
        MachineSchedule.scheduled_start < schedule.scheduled_end,
        MachineSchedule.scheduled_end > schedule.scheduled_start,
    ).first()

    if conflict:
        raise HTTPException(status_code=400, detail="Scheduling conflict detected")

    db_schedule = MachineSchedule(
        machine_id=schedule.machine_id,
        work_order_id=schedule.work_order_id,
        scheduled_start=schedule.scheduled_start,
        scheduled_end=schedule.scheduled_end,
        planned_hours=schedule.planned_hours,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_schedule)

    # Update machine status
    machine.status = "in_use"

    db.commit()
    db.refresh(db_schedule)
    return db_schedule


@router.get("/machine-schedules", response_model=List[MachineScheduleResponse])
def list_machine_schedules(
    machine_id: Optional[int] = None,
    work_order_id: Optional[int] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List machine schedules."""
    query = db.query(MachineSchedule)
    query = apply_tenant_filter(query, MachineSchedule, tenant_id)
    if machine_id:
        query = query.filter(MachineSchedule.machine_id == machine_id)
    if work_order_id:
        query = query.filter(MachineSchedule.work_order_id == work_order_id)
    return query.order_by(MachineSchedule.scheduled_start).all()


# ============================================================================
# Process 35: Labor Allocation
# ============================================================================

@router.post("/labor-allocations", response_model=LaborAllocationResponse)
def create_labor_allocation(
    allocation: LaborAllocationCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """
    Process 35: Labor Allocation
    Input: Work orders, worker availability
    Output: Labor assignment
    """
    # Verify work order exists
    wo = db.query(WorkOrder).filter(WorkOrder.id == allocation.work_order_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")

    db_allocation = LaborAllocation(
        worker_id=allocation.worker_id,
        work_order_id=allocation.work_order_id,
        role=allocation.role,
        skill_level=allocation.skill_level,
        scheduled_start=allocation.scheduled_start,
        scheduled_end=allocation.scheduled_end,
        planned_hours=allocation.planned_hours,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_allocation)
    db.commit()
    db.refresh(db_allocation)
    return db_allocation


@router.get("/labor-allocations", response_model=List[LaborAllocationResponse])
def list_labor_allocations(
    worker_id: Optional[int] = None,
    work_order_id: Optional[int] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List labor allocations."""
    query = db.query(LaborAllocation)
    query = apply_tenant_filter(query, LaborAllocation, tenant_id)
    if worker_id:
        query = query.filter(LaborAllocation.worker_id == worker_id)
    if work_order_id:
        query = query.filter(LaborAllocation.work_order_id == work_order_id)
    return query.order_by(LaborAllocation.scheduled_start).all()


# ============================================================================
# Process 36: Shopfloor Job Assignment
# ============================================================================

@router.post("/shopfloor-jobs", response_model=ShopfloorJobResponse)
def create_shopfloor_job(
    job: ShopfloorJobCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """
    Process 36: Shopfloor Job Assignment
    Input: Schedule → Assign worker
    Output: Job assignment
    """
    # Generate job number
    count = db.query(ShopfloorJob).count()
    job_number = f"JOB-{datetime.now().year}-{count + 1:05d}"

    db_job = ShopfloorJob(
        job_number=job_number,
        work_order_id=job.work_order_id,
        worker_id=job.worker_id,
        machine_id=job.machine_id,
        operation_name=job.operation_name,
        operation_sequence=job.operation_sequence,
        quantity_assigned=job.quantity_assigned,
        assigned_at=job.assigned_at,
        notes=job.notes,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@router.get("/shopfloor-jobs", response_model=List[ShopfloorJobResponse])
def list_shopfloor_jobs(
    worker_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List shopfloor jobs."""
    query = db.query(ShopfloorJob)
    query = apply_tenant_filter(query, ShopfloorJob, tenant_id)
    if worker_id:
        query = query.filter(ShopfloorJob.worker_id == worker_id)
    if status:
        query = query.filter(ShopfloorJob.status == status)
    return query.order_by(ShopfloorJob.assigned_at.desc()).all()


@router.post("/shopfloor-jobs/{job_id}/start")
def start_shopfloor_job(
    job_id: int,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """Start a shopfloor job."""
    job = db.query(ShopfloorJob).filter(ShopfloorJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = "in_progress"
    job.started_at = datetime.utcnow()
    db.commit()
    return {"message": "Job started", "job_number": job.job_number}


@router.post("/shopfloor-jobs/{job_id}/complete")
def complete_shopfloor_job(
    job_id: int,
    quantity_completed: float,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """Complete a shopfloor job."""
    job = db.query(ShopfloorJob).filter(ShopfloorJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = "completed"
    job.quantity_completed = quantity_completed
    job.completed_at = datetime.utcnow()
    db.commit()
    return {"message": "Job completed", "job_number": job.job_number}


# ============================================================================
# Process 37: Production Execution
# ============================================================================

@router.post("/production-executions", response_model=ProductionExecutionResponse)
def create_production_execution(
    execution: ProductionExecutionCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """
    Process 37: Production Execution
    Input: Job, materials → Production activity
    Output: Production record
    """
    # Verify work order exists
    wo = db.query(WorkOrder).filter(WorkOrder.id == execution.work_order_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")

    db_execution = ProductionExecution(
        work_order_id=execution.work_order_id,
        job_id=execution.job_id,
        quantity_produced=execution.quantity_produced,
        quantity_good=execution.quantity_good,
        quantity_rejected=execution.quantity_rejected,
        execution_date=execution.execution_date,
        duration_hours=execution.duration_hours,
        operator_id=execution.operator_id,
        machine_id=execution.machine_id,
        notes=execution.notes,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_execution)

    # Update work order quantities
    wo.quantity_produced += execution.quantity_produced

    db.commit()
    db.refresh(db_execution)
    return db_execution


@router.get("/production-executions", response_model=List[ProductionExecutionResponse])
def list_production_executions(
    work_order_id: Optional[int] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List production executions."""
    query = db.query(ProductionExecution)
    query = apply_tenant_filter(query, ProductionExecution, tenant_id)
    if work_order_id:
        query = query.filter(ProductionExecution.work_order_id == work_order_id)
    return query.order_by(ProductionExecution.execution_date.desc()).all()


# ============================================================================
# Process 38: Work Order Tracking
# ============================================================================

@router.get("/work-orders/{wo_id}/status")
def get_work_order_status(
    wo_id: int,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """
    Process 38: Work Order Tracking
    Get detailed work order status and progress
    """
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")

    # Get related data
    material_issues = db.query(MaterialIssue).filter(
        MaterialIssue.work_order_id == wo_id
    ).all()

    executions = db.query(ProductionExecution).filter(
        ProductionExecution.work_order_id == wo_id
    ).all()

    quality_checks = db.query(QualityCheckProduction).filter(
        QualityCheckProduction.work_order_id == wo_id
    ).all()

    progress_percent = (wo.quantity_produced / wo.quantity_planned * 100) if wo.quantity_planned > 0 else 0

    return {
        "work_order": wo,
        "progress_percent": round(progress_percent, 2),
        "material_issues_count": len(material_issues),
        "executions_count": len(executions),
        "quality_checks_count": len(quality_checks),
        "status": wo.status,
    }


# ============================================================================
# Process 39: Downtime Logging
# ============================================================================

@router.post("/downtimes", response_model=DowntimeResponse)
def create_downtime(
    downtime: DowntimeCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """
    Process 39: Downtime Logging
    Input: Downtime event → Log downtime
    Output: Downtime record
    """
    # Verify machine exists
    machine = db.query(Machine).filter(Machine.id == downtime.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    db_downtime = Downtime(
        machine_id=downtime.machine_id,
        work_order_id=downtime.work_order_id,
        downtime_type=downtime.downtime_type,
        reason=downtime.reason,
        description=downtime.description,
        start_time=downtime.start_time,
        reported_by_id=downtime.reported_by_id,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_downtime)

    # Update machine status
    if downtime.downtime_type == "breakdown":
        machine.status = "breakdown"

    db.commit()
    db.refresh(db_downtime)
    return db_downtime


@router.get("/downtimes", response_model=List[DowntimeResponse])
def list_downtimes(
    machine_id: Optional[int] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List downtimes."""
    query = db.query(Downtime)
    query = apply_tenant_filter(query, Downtime, tenant_id)
    if machine_id:
        query = query.filter(Downtime.machine_id == machine_id)
    return query.order_by(Downtime.start_time.desc()).all()


@router.post("/downtimes/{downtime_id}/resolve")
def resolve_downtime(
    downtime_id: int,
    resolution: str,
    resolved_by_id: int,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """Resolve a downtime event."""
    downtime = db.query(Downtime).filter(Downtime.id == downtime_id).first()
    if not downtime:
        raise HTTPException(status_code=404, detail="Downtime not found")

    downtime.end_time = datetime.utcnow()
    downtime.duration_hours = (downtime.end_time - downtime.start_time).total_seconds() / 3600
    downtime.resolution = resolution
    downtime.resolved_by_id = resolved_by_id

    # Update machine status back to available
    machine = db.query(Machine).filter(Machine.id == downtime.machine_id).first()
    if machine:
        machine.status = "available"

    db.commit()
    return {"message": "Downtime resolved", "duration_hours": downtime.duration_hours}


# ============================================================================
# Process 40: Quality Check
# ============================================================================

@router.post("/quality-checks-production", response_model=QualityCheckProductionResponse)
def create_quality_check_production(
    qc: QualityCheckProductionCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """
    Process 40: Quality Check
    Input: Production output → Inspect
    Output: Quality result
    """
    # Generate check number
    count = db.query(QualityCheckProduction).count()
    check_number = f"QC-PROD-{datetime.now().year}-{count + 1:05d}"

    db_qc = QualityCheckProduction(
        check_number=check_number,
        work_order_id=qc.work_order_id,
        execution_id=qc.execution_id,
        check_type=qc.check_type,
        check_point=qc.check_point,
        sample_size=qc.sample_size,
        inspection_date=qc.inspection_date,
        inspector_id=qc.inspector_id,
        notes=qc.notes,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_qc)
    db.commit()
    db.refresh(db_qc)
    return db_qc


@router.get("/quality-checks-production", response_model=List[QualityCheckProductionResponse])
def list_quality_checks_production(
    work_order_id: Optional[int] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List quality checks for production."""
    query = db.query(QualityCheckProduction)
    query = apply_tenant_filter(query, QualityCheckProduction, tenant_id)
    if work_order_id:
        query = query.filter(QualityCheckProduction.work_order_id == work_order_id)
    return query.order_by(QualityCheckProduction.inspection_date.desc()).all()


@router.post("/quality-checks-production/{qc_id}/record-result")
def record_quality_check_result(
    qc_id: int,
    quantity_passed: float,
    quantity_failed: float,
    result: str,
    defects_found: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """Record quality check results."""
    qc = db.query(QualityCheckProduction).filter(QualityCheckProduction.id == qc_id).first()
    if not qc:
        raise HTTPException(status_code=404, detail="Quality check not found")

    qc.quantity_passed = quantity_passed
    qc.quantity_failed = quantity_failed
    qc.result = result
    qc.defects_found = defects_found
    db.commit()

    return {
        "message": "Quality check result recorded",
        "check_number": qc.check_number,
        "result": result,
    }


# ============================================================================
# Process 41: Rework Processing
# ============================================================================

@router.post("/rework-orders", response_model=ReworkOrderResponse)
def create_rework_order(
    rework: ReworkOrderCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """
    Process 41: Rework Processing
    Input: Failed QC → Create rework order
    Output: Rework order
    """
    # Generate rework number
    count = db.query(ReworkOrder).count()
    rework_number = f"RWK-{datetime.now().year}-{count + 1:05d}"

    db_rework = ReworkOrder(
        rework_number=rework_number,
        work_order_id=rework.work_order_id,
        quality_check_id=rework.quality_check_id,
        product_id=rework.product_id,
        quantity_to_rework=rework.quantity_to_rework,
        defect_description=rework.defect_description,
        rework_instructions=rework.rework_instructions,
        estimated_cost=rework.estimated_cost,
        assigned_to_id=rework.assigned_to_id,
        notes=rework.notes,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_rework)
    db.commit()
    db.refresh(db_rework)
    return db_rework


@router.get("/rework-orders", response_model=List[ReworkOrderResponse])
def list_rework_orders(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List rework orders."""
    query = db.query(ReworkOrder)
    query = apply_tenant_filter(query, ReworkOrder, tenant_id)
    if status:
        query = query.filter(ReworkOrder.status == status)
    return query.order_by(ReworkOrder.created_at.desc()).all()


@router.post("/rework-orders/{rework_id}/complete")
def complete_rework_order(
    rework_id: int,
    quantity_completed: float,
    quantity_scrapped: float,
    actual_cost: float,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """Complete a rework order."""
    rework = db.query(ReworkOrder).filter(ReworkOrder.id == rework_id).first()
    if not rework:
        raise HTTPException(status_code=404, detail="Rework order not found")

    rework.status = "completed"
    rework.quantity_completed = quantity_completed
    rework.quantity_scrapped = quantity_scrapped
    rework.actual_cost = actual_cost
    db.commit()
    return {"message": "Rework order completed", "rework_number": rework.rework_number}


# ============================================================================
# Process 42: Scrap Recording
# ============================================================================

@router.post("/scrap-records", response_model=ScrapRecordResponse)
def create_scrap_record(
    scrap: ScrapRecordCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """
    Process 42: Scrap Recording
    Input: Scrap event → Record scrap
    Output: Scrap record
    """
    # Generate scrap number
    count = db.query(ScrapRecord).count()
    scrap_number = f"SCR-{datetime.now().year}-{count + 1:05d}"

    total_cost = scrap.quantity_scrapped * scrap.unit_cost

    db_scrap = ScrapRecord(
        scrap_number=scrap_number,
        work_order_id=scrap.work_order_id,
        product_id=scrap.product_id,
        quantity_scrapped=scrap.quantity_scrapped,
        scrap_reason=scrap.scrap_reason,
        description=scrap.description,
        unit_cost=scrap.unit_cost,
        total_cost=total_cost,
        recorded_by_id=scrap.recorded_by_id,
        scrap_date=scrap.scrap_date,
        disposal_method=scrap.disposal_method,
        notes=scrap.notes,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_scrap)

    # Update work order scrap quantity if linked
    if scrap.work_order_id:
        wo = db.query(WorkOrder).filter(WorkOrder.id == scrap.work_order_id).first()
        if wo:
            wo.quantity_scrapped += scrap.quantity_scrapped

    db.commit()
    db.refresh(db_scrap)
    return db_scrap


@router.get("/scrap-records", response_model=List[ScrapRecordResponse])
def list_scrap_records(
    work_order_id: Optional[int] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List scrap records."""
    query = db.query(ScrapRecord)
    query = apply_tenant_filter(query, ScrapRecord, tenant_id)
    if work_order_id:
        query = query.filter(ScrapRecord.work_order_id == work_order_id)
    return query.order_by(ScrapRecord.scrap_date.desc()).all()


# ============================================================================
# Process 43: Finished Goods Receipt
# ============================================================================

@router.post("/finished-goods-receipts", response_model=FinishedGoodsReceiptResponse)
def create_finished_goods_receipt(
    receipt: FinishedGoodsReceiptCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """
    Process 43: Finished Goods Receipt
    Input: Completed WO → Receive finished goods
    Output: FG inventory update
    """
    # Verify work order exists and is ready
    wo = db.query(WorkOrder).filter(WorkOrder.id == receipt.work_order_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")

    # Generate receipt number
    count = db.query(FinishedGoodsReceipt).count()
    receipt_number = f"FGR-{datetime.now().year}-{count + 1:05d}"

    total_cost = receipt.quantity_received * receipt.unit_cost

    db_receipt = FinishedGoodsReceipt(
        receipt_number=receipt_number,
        work_order_id=receipt.work_order_id,
        product_id=receipt.product_id,
        quantity_received=receipt.quantity_received,
        location_id=receipt.location_id,
        unit_cost=receipt.unit_cost,
        total_cost=total_cost,
        notes=receipt.notes,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_receipt)
    db.commit()
    db.refresh(db_receipt)
    return db_receipt


@router.get("/finished-goods-receipts", response_model=List[FinishedGoodsReceiptResponse])
def list_finished_goods_receipts(
    work_order_id: Optional[int] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List finished goods receipts."""
    query = db.query(FinishedGoodsReceipt)
    query = apply_tenant_filter(query, FinishedGoodsReceipt, tenant_id)
    if work_order_id:
        query = query.filter(FinishedGoodsReceipt.work_order_id == work_order_id)
    return query.order_by(FinishedGoodsReceipt.created_at.desc()).all()


@router.post("/finished-goods-receipts/{receipt_id}/receive")
def receive_finished_goods(
    receipt_id: int,
    received_by_id: int,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """Receive finished goods into inventory."""
    receipt = db.query(FinishedGoodsReceipt).filter(
        FinishedGoodsReceipt.id == receipt_id
    ).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    receipt.status = "received"
    receipt.received_by_id = received_by_id
    receipt.received_date = datetime.utcnow()

    # Update work order status if fully received
    wo = db.query(WorkOrder).filter(WorkOrder.id == receipt.work_order_id).first()
    if wo and wo.quantity_produced >= wo.quantity_planned:
        wo.status = "completed"
        wo.actual_end = datetime.utcnow()

    db.commit()
    return {"message": "Finished goods received", "receipt_number": receipt.receipt_number}


@router.post("/finished-goods-receipts/{receipt_id}/put-away")
def put_away_finished_goods(
    receipt_id: int,
    location_id: int,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """Put away finished goods to stock location."""
    receipt = db.query(FinishedGoodsReceipt).filter(
        FinishedGoodsReceipt.id == receipt_id
    ).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    # Update or create stock item
    stock_item = db.query(StockItem).filter(
        StockItem.product_id == receipt.product_id,
        StockItem.location_id == location_id
    ).first()

    if stock_item:
        stock_item.quantity += receipt.quantity_received
    else:
        stock_item = StockItem(
            product_id=receipt.product_id,
            location_id=location_id,
            quantity=receipt.quantity_received,
            unit_cost=receipt.unit_cost,
            tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
        )
        db.add(stock_item)

    receipt.status = "put_away"
    receipt.location_id = location_id

    db.commit()
    return {"message": "Finished goods put away", "receipt_number": receipt.receipt_number}


# ============================================================================
# Process 44: Maintenance Request
# ============================================================================

@router.post("/maintenance-requests", response_model=MaintenanceRequestResponse)
def create_maintenance_request(
    request: MaintenanceRequestCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """
    Process 44: Maintenance Request
    Input: Machine issue → Request maintenance
    Output: Maintenance request
    """
    # Verify machine exists
    machine = db.query(Machine).filter(Machine.id == request.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    # Generate request number
    count = db.query(MaintenanceRequest).count()
    request_number = f"MR-{datetime.now().year}-{count + 1:05d}"

    db_request = MaintenanceRequest(
        request_number=request_number,
        machine_id=request.machine_id,
        issue_description=request.issue_description,
        priority=request.priority,
        requested_by_id=request.requested_by_id,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_request)

    # Update machine status if urgent
    if request.priority == "urgent":
        machine.status = "maintenance"

    db.commit()
    db.refresh(db_request)
    return db_request


@router.get("/maintenance-requests", response_model=List[MaintenanceRequestResponse])
def list_maintenance_requests(
    machine_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List maintenance requests."""
    query = db.query(MaintenanceRequest)
    query = apply_tenant_filter(query, MaintenanceRequest, tenant_id)
    if machine_id:
        query = query.filter(MaintenanceRequest.machine_id == machine_id)
    if status:
        query = query.filter(MaintenanceRequest.status == status)
    return query.order_by(MaintenanceRequest.created_at.desc()).all()


@router.post("/maintenance-requests/{request_id}/complete")
def complete_maintenance_request(
    request_id: int,
    work_performed: str,
    resolution_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """Complete a maintenance request."""
    request = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.id == request_id
    ).first()
    if not request:
        raise HTTPException(status_code=404, detail="Maintenance request not found")

    request.status = "completed"
    request.work_performed = work_performed
    request.resolution_notes = resolution_notes
    request.completed_date = datetime.utcnow()

    # Update machine status back to available
    machine = db.query(Machine).filter(Machine.id == request.machine_id).first()
    if machine:
        machine.status = "available"

    db.commit()
    return {"message": "Maintenance request completed", "request_number": request.request_number}


# ============================================================================
# Process 45: Preventive Maintenance
# ============================================================================

@router.post("/preventive-maintenances", response_model=PreventiveMaintenanceResponse)
def create_preventive_maintenance(
    pm: PreventiveMaintenanceCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """
    Process 45: Preventive Maintenance
    Input: Maintenance schedule → Schedule PM
    Output: PM record
    """
    # Verify machine exists
    machine = db.query(Machine).filter(Machine.id == pm.machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    # Generate PM number
    count = db.query(PreventiveMaintenance).count()
    pm_number = f"PM-{datetime.now().year}-{count + 1:05d}"

    db_pm = PreventiveMaintenance(
        pm_number=pm_number,
        machine_id=pm.machine_id,
        pm_type=pm.pm_type,
        description=pm.description,
        checklist=pm.checklist,
        scheduled_date=pm.scheduled_date,
        frequency_days=pm.frequency_days,
        assigned_to_id=pm.assigned_to_id,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_pm)
    db.commit()
    db.refresh(db_pm)
    return db_pm


@router.get("/preventive-maintenances", response_model=List[PreventiveMaintenanceResponse])
def list_preventive_maintenances(
    machine_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List preventive maintenances."""
    query = db.query(PreventiveMaintenance)
    query = apply_tenant_filter(query, PreventiveMaintenance, tenant_id)
    if machine_id:
        query = query.filter(PreventiveMaintenance.machine_id == machine_id)
    if status:
        query = query.filter(PreventiveMaintenance.status == status)
    return query.order_by(PreventiveMaintenance.scheduled_date).all()


@router.post("/preventive-maintenances/{pm_id}/complete")
def complete_preventive_maintenance(
    pm_id: int,
    work_performed: str,
    parts_replaced: Optional[str] = None,
    findings: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """Complete a preventive maintenance."""
    pm = db.query(PreventiveMaintenance).filter(PreventiveMaintenance.id == pm_id).first()
    if not pm:
        raise HTTPException(status_code=404, detail="PM not found")

    pm.status = "completed"
    pm.actual_end = datetime.utcnow()
    if pm.actual_start:
        pm.duration_hours = (pm.actual_end - pm.actual_start).total_seconds() / 3600
    pm.work_performed = work_performed
    pm.parts_replaced = parts_replaced
    pm.findings = findings

    # Schedule next PM if frequency is set
    if pm.frequency_days:
        from datetime import timedelta
        pm.next_pm_date = pm.scheduled_date + timedelta(days=pm.frequency_days)

    # Update machine maintenance dates
    machine = db.query(Machine).filter(Machine.id == pm.machine_id).first()
    if machine:
        machine.last_maintenance_date = pm.actual_end
        machine.next_maintenance_date = pm.next_pm_date

    db.commit()
    return {
        "message": "PM completed",
        "pm_number": pm.pm_number,
        "next_pm_date": pm.next_pm_date,
    }


# ============================================================================
# Summary & Analytics Endpoints
# ============================================================================

@router.get("/manufacturing/dashboard")
def get_manufacturing_dashboard(
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """Get manufacturing dashboard summary."""
    # Work order statistics
    wo_query = db.query(WorkOrder)
    wo_query = apply_tenant_filter(wo_query, WorkOrder, tenant_id)

    total_wos = wo_query.count()
    active_wos = wo_query.filter(WorkOrder.status == "in_progress").count()
    completed_wos = wo_query.filter(WorkOrder.status == "completed").count()

    # Machine statistics
    machine_query = db.query(Machine)
    machine_query = apply_tenant_filter(machine_query, Machine, tenant_id)

    total_machines = machine_query.count()
    available_machines = machine_query.filter(Machine.status == "available").count()
    in_use_machines = machine_query.filter(Machine.status == "in_use").count()
    breakdown_machines = machine_query.filter(Machine.status == "breakdown").count()

    # Quality statistics
    qc_query = db.query(QualityCheckProduction)
    qc_query = apply_tenant_filter(qc_query, QualityCheckProduction, tenant_id)

    total_qc_checks = qc_query.count()
    passed_qc = qc_query.filter(QualityCheckProduction.result == "pass").count()
    failed_qc = qc_query.filter(QualityCheckProduction.result == "fail").count()

    # Maintenance statistics
    mr_query = db.query(MaintenanceRequest)
    mr_query = apply_tenant_filter(mr_query, MaintenanceRequest, tenant_id)

    open_maintenance_requests = mr_query.filter(
        MaintenanceRequest.status.in_(["submitted", "approved", "scheduled"])
    ).count()

    return {
        "work_orders": {
            "total": total_wos,
            "active": active_wos,
            "completed": completed_wos,
        },
        "machines": {
            "total": total_machines,
            "available": available_machines,
            "in_use": in_use_machines,
            "breakdown": breakdown_machines,
        },
        "quality": {
            "total_checks": total_qc_checks,
            "passed": passed_qc,
            "failed": failed_qc,
            "pass_rate": round((passed_qc / total_qc_checks * 100) if total_qc_checks > 0 else 0, 2),
        },
        "maintenance": {
            "open_requests": open_maintenance_requests,
        },
    }
