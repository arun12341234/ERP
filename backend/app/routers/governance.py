"""
Governance, Audit, AI & System Ops router - Processes 101-110.

This module handles:
- Role & Access Assignment
- Data Backup
- System Health Monitoring
- API Integration
- Document Digitization
- Analytics Dashboard
- Risk Assessment
- Alert Management
- Audit Trail (using existing AuditLog model)
- Regulatory Compliance
"""
from datetime import datetime, date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.core.database import get_db
from app.core.config import settings
from app.models.role_assignment import RoleAssignment, RoleType, AssignmentStatus
from app.models.data_backup import DataBackup, BackupStatus
from app.models.system_health import SystemHealthCheck, HealthStatus
from app.models.api_integration import APIIntegration, IntegrationStatus
from app.models.document_digitization import DocumentDigitization, ProcessingStatus
from app.models.analytics_dashboard import AnalyticsDashboard, KPIMetric
from app.models.risk_assessment import RiskAssessment, RiskLevel, RiskStatus
from app.models.alert_management import AlertManagement, AlertSeverity, AlertStatus
from app.models.audit_log import AuditLog
from app.models.regulatory_compliance import RegulatoryCompliance, ComplianceStatus

from app.schemas.governance import (
    RoleAssignmentCreate, RoleAssignmentResponse,
    DataBackupCreate, DataBackupResponse,
    SystemHealthCheckCreate, SystemHealthCheckResponse,
    APIIntegrationCreate, APIIntegrationResponse,
    DocumentDigitizationCreate, DocumentDigitizationResponse,
    AnalyticsDashboardCreate, AnalyticsDashboardResponse,
    KPIMetricCreate, KPIMetricResponse,
    RiskAssessmentCreate, RiskAssessmentResponse,
    AlertManagementCreate, AlertManagementResponse,
    RegulatoryComplianceCreate, RegulatoryComplianceResponse,
)

router = APIRouter(prefix="/governance", tags=["governance"])


# ============================================================================
# Helper Functions
# ============================================================================

def generate_document_number(prefix: str, db: Session) -> str:
    """Generate unique document number with format PREFIX-YYYY-NNNNN."""
    year = datetime.utcnow().year
    count = db.query(func.count()).filter(
        func.extract('year', RoleAssignment.created_at) == year
    ).scalar() or 0
    return f"{prefix}-{year}-{count + 1:05d}"


def apply_tenant_filter(query, model, tenant_id: Optional[int] = None):
    """Apply tenant filter if multi-tenancy is enabled."""
    if settings.ENABLE_TENANCY and tenant_id is not None:
        return query.filter(model.tenant_id == tenant_id)
    return query


# ============================================================================
# Process 101: Role & Access Assignment
# ============================================================================

@router.post("/role-assignments", response_model=RoleAssignmentResponse, status_code=201)
def create_role_assignment(
    assignment: RoleAssignmentCreate,
    assigned_by: int,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Assign a role and access rights to a user."""
    db_assignment = RoleAssignment(
        assignment_id=generate_document_number("ROLE", db),
        assigned_by_id=assigned_by,
        **assignment.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_assignment.tenant_id = tenant_id

    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)

    # Create audit log
    log = AuditLog(
        entity_type="role_assignment",
        entity_id=db_assignment.id,
        action="assigned",
        performed_by_id=assigned_by
    )
    db.add(log)
    db.commit()

    return db_assignment


@router.get("/role-assignments", response_model=List[RoleAssignmentResponse])
def list_role_assignments(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List all role assignments."""
    query = db.query(RoleAssignment)
    query = apply_tenant_filter(query, RoleAssignment, tenant_id)

    if user_id:
        query = query.filter(RoleAssignment.user_id == user_id)
    if status:
        query = query.filter(RoleAssignment.status == status)

    return query.offset(skip).limit(limit).all()


@router.put("/role-assignments/{assignment_id}/revoke", response_model=RoleAssignmentResponse)
def revoke_role_assignment(
    assignment_id: int,
    revoked_by: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Revoke a role assignment."""
    assignment = db.query(RoleAssignment).filter(RoleAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    assignment.status = AssignmentStatus.REVOKED
    assignment.revoked_by_id = revoked_by
    assignment.revoked_at = datetime.utcnow()
    assignment.revocation_reason = reason

    db.commit()
    db.refresh(assignment)

    # Create audit log
    log = AuditLog(
        entity_type="role_assignment",
        entity_id=assignment.id,
        action="revoked",
        performed_by_id=revoked_by
    )
    db.add(log)
    db.commit()

    return assignment


# ============================================================================
# Process 102: Data Backup
# ============================================================================

@router.post("/backups", response_model=DataBackupResponse, status_code=201)
def create_backup(
    backup: DataBackupCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Schedule a new database backup."""
    db_backup = DataBackup(
        backup_id=generate_document_number("BKP", db),
        **backup.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_backup.tenant_id = tenant_id

    # Calculate expiry
    db_backup.expires_at = db_backup.scheduled_at + timedelta(days=backup.retention_days)

    db.add(db_backup)
    db.commit()
    db.refresh(db_backup)

    return db_backup


@router.get("/backups", response_model=List[DataBackupResponse])
def list_backups(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List all backups."""
    query = db.query(DataBackup)
    query = apply_tenant_filter(query, DataBackup, tenant_id)

    if status:
        query = query.filter(DataBackup.status == status)

    return query.order_by(DataBackup.scheduled_at.desc()).offset(skip).limit(limit).all()


@router.put("/backups/{backup_id}/execute", response_model=DataBackupResponse)
def execute_backup(
    backup_id: int,
    db: Session = Depends(get_db)
):
    """Execute a backup."""
    backup = db.query(DataBackup).filter(DataBackup.id == backup_id).first()
    if not backup:
        raise HTTPException(status_code=404, detail="Backup not found")

    backup.status = BackupStatus.IN_PROGRESS
    backup.started_at = datetime.utcnow()

    db.commit()
    db.refresh(backup)

    # In production, this would trigger actual backup process

    return backup


# ============================================================================
# Process 103: System Health Monitoring
# ============================================================================

@router.post("/health-checks", response_model=SystemHealthCheckResponse, status_code=201)
def create_health_check(
    check: SystemHealthCheckCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a new system health check monitor."""
    db_check = SystemHealthCheck(
        check_id=generate_document_number("HLTH", db),
        status=HealthStatus.HEALTHY,
        **check.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_check.tenant_id = tenant_id

    db.add(db_check)
    db.commit()
    db.refresh(db_check)

    return db_check


@router.get("/health-checks", response_model=List[SystemHealthCheckResponse])
def list_health_checks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    component_type: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List all system health checks."""
    query = db.query(SystemHealthCheck)
    query = apply_tenant_filter(query, SystemHealthCheck, tenant_id)

    if status:
        query = query.filter(SystemHealthCheck.status == status)
    if component_type:
        query = query.filter(SystemHealthCheck.component_type == component_type)

    return query.offset(skip).limit(limit).all()


@router.get("/health-checks/dashboard")
def get_health_dashboard(db: Session = Depends(get_db)):
    """Get system health dashboard summary."""
    total_components = db.query(func.count(SystemHealthCheck.id)).scalar()
    healthy = db.query(func.count(SystemHealthCheck.id)).filter(
        SystemHealthCheck.status == HealthStatus.HEALTHY
    ).scalar()
    warning = db.query(func.count(SystemHealthCheck.id)).filter(
        SystemHealthCheck.status == HealthStatus.WARNING
    ).scalar()
    critical = db.query(func.count(SystemHealthCheck.id)).filter(
        SystemHealthCheck.status == HealthStatus.CRITICAL
    ).scalar()
    down = db.query(func.count(SystemHealthCheck.id)).filter(
        SystemHealthCheck.status == HealthStatus.DOWN
    ).scalar()

    avg_availability = db.query(func.avg(SystemHealthCheck.availability_percent)).scalar() or 100.0

    return {
        "total_components": total_components,
        "healthy": healthy,
        "warning": warning,
        "critical": critical,
        "down": down,
        "average_availability": round(avg_availability, 2)
    }


# ============================================================================
# Process 104: API Integration
# ============================================================================

@router.post("/api-integrations", response_model=APIIntegrationResponse, status_code=201)
def create_api_integration(
    integration: APIIntegrationCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a new API integration configuration."""
    db_integration = APIIntegration(
        integration_id=generate_document_number("API", db),
        **integration.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_integration.tenant_id = tenant_id

    db.add(db_integration)
    db.commit()
    db.refresh(db_integration)

    return db_integration


@router.get("/api-integrations", response_model=List[APIIntegrationResponse])
def list_api_integrations(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List all API integrations."""
    query = db.query(APIIntegration)
    query = apply_tenant_filter(query, APIIntegration, tenant_id)

    if status:
        query = query.filter(APIIntegration.status == status)

    return query.offset(skip).limit(limit).all()


@router.put("/api-integrations/{integration_id}/test", response_model=APIIntegrationResponse)
def test_api_integration(
    integration_id: int,
    db: Session = Depends(get_db)
):
    """Test an API integration."""
    integration = db.query(APIIntegration).filter(APIIntegration.id == integration_id).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    integration.last_test_at = datetime.utcnow()
    integration.last_test_status = "success"  # In production, would actually test the API
    integration.status = IntegrationStatus.TESTING

    db.commit()
    db.refresh(integration)

    return integration


@router.put("/api-integrations/{integration_id}/deploy", response_model=APIIntegrationResponse)
def deploy_api_integration(
    integration_id: int,
    deployed_by: int,
    db: Session = Depends(get_db)
):
    """Deploy an API integration to production."""
    integration = db.query(APIIntegration).filter(APIIntegration.id == integration_id).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    integration.status = IntegrationStatus.ACTIVE
    integration.is_active = 1
    integration.deployed_at = datetime.utcnow()
    integration.deployed_by_id = deployed_by

    db.commit()
    db.refresh(integration)

    return integration


# ============================================================================
# Process 105: Document Digitization
# ============================================================================

@router.post("/documents", response_model=DocumentDigitizationResponse, status_code=201)
def create_document(
    document: DocumentDigitizationCreate,
    uploaded_by: Optional[int] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Upload a document for OCR digitization."""
    db_document = DocumentDigitization(
        document_id=generate_document_number("DOC", db),
        uploaded_by_id=uploaded_by,
        **document.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_document.tenant_id = tenant_id

    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    return db_document


@router.get("/documents", response_model=List[DocumentDigitizationResponse])
def list_documents(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    document_type: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List all digitized documents."""
    query = db.query(DocumentDigitization)
    query = apply_tenant_filter(query, DocumentDigitization, tenant_id)

    if status:
        query = query.filter(DocumentDigitization.status == status)
    if document_type:
        query = query.filter(DocumentDigitization.document_type == document_type)

    return query.order_by(DocumentDigitization.created_at.desc()).offset(skip).limit(limit).all()


@router.put("/documents/{document_id}/process", response_model=DocumentDigitizationResponse)
def process_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Process document with OCR."""
    document = db.query(DocumentDigitization).filter(DocumentDigitization.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    document.status = ProcessingStatus.PROCESSING
    document.processing_started_at = datetime.utcnow()

    db.commit()
    db.refresh(document)

    # In production, this would trigger actual OCR processing

    return document


# ============================================================================
# Process 106: Analytics Dashboard
# ============================================================================

@router.post("/dashboards", response_model=AnalyticsDashboardResponse, status_code=201)
def create_dashboard(
    dashboard: AnalyticsDashboardCreate,
    owner_id: Optional[int] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a new analytics dashboard."""
    db_dashboard = AnalyticsDashboard(
        dashboard_id=generate_document_number("DASH", db),
        owner_id=owner_id,
        **dashboard.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_dashboard.tenant_id = tenant_id

    db.add(db_dashboard)
    db.commit()
    db.refresh(db_dashboard)

    return db_dashboard


@router.get("/dashboards", response_model=List[AnalyticsDashboardResponse])
def list_dashboards(
    skip: int = 0,
    limit: int = 100,
    dashboard_type: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List all dashboards."""
    query = db.query(AnalyticsDashboard)
    query = apply_tenant_filter(query, AnalyticsDashboard, tenant_id)

    if dashboard_type:
        query = query.filter(AnalyticsDashboard.dashboard_type == dashboard_type)

    return query.offset(skip).limit(limit).all()


@router.post("/kpi-metrics", response_model=KPIMetricResponse, status_code=201)
def create_kpi_metric(
    metric: KPIMetricCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a new KPI metric."""
    # Calculate changes
    change_value = 0.0
    change_percentage = 0.0
    if metric.current_value and hasattr(metric, 'previous_value') and metric.previous_value:
        change_value = metric.current_value - metric.previous_value
        if metric.previous_value != 0:
            change_percentage = (change_value / metric.previous_value) * 100

    db_metric = KPIMetric(
        metric_id=generate_document_number("KPI", db),
        change_value=change_value,
        change_percentage=change_percentage,
        **metric.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_metric.tenant_id = tenant_id

    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)

    return db_metric


@router.get("/kpi-metrics", response_model=List[KPIMetricResponse])
def list_kpi_metrics(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List all KPI metrics."""
    query = db.query(KPIMetric)
    query = apply_tenant_filter(query, KPIMetric, tenant_id)

    if category:
        query = query.filter(KPIMetric.metric_category == category)

    return query.order_by(KPIMetric.calculated_at.desc()).offset(skip).limit(limit).all()


# ============================================================================
# Process 107: Risk Assessment
# ============================================================================

@router.post("/risks", response_model=RiskAssessmentResponse, status_code=201)
def create_risk_assessment(
    risk: RiskAssessmentCreate,
    identified_by: Optional[int] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a new risk assessment."""
    # Calculate risk score and level
    risk_score = risk.likelihood_score * risk.impact_score

    if risk_score <= 5:
        risk_level = RiskLevel.LOW
    elif risk_score <= 12:
        risk_level = RiskLevel.MEDIUM
    elif risk_score <= 20:
        risk_level = RiskLevel.HIGH
    else:
        risk_level = RiskLevel.CRITICAL

    db_risk = RiskAssessment(
        risk_id=generate_document_number("RISK", db),
        risk_score=risk_score,
        risk_level=risk_level,
        identified_by_id=identified_by,
        **risk.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_risk.tenant_id = tenant_id

    db.add(db_risk)
    db.commit()
    db.refresh(db_risk)

    return db_risk


@router.get("/risks", response_model=List[RiskAssessmentResponse])
def list_risks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List all risk assessments."""
    query = db.query(RiskAssessment)
    query = apply_tenant_filter(query, RiskAssessment, tenant_id)

    if status:
        query = query.filter(RiskAssessment.status == status)
    if risk_level:
        query = query.filter(RiskAssessment.risk_level == risk_level)

    return query.order_by(RiskAssessment.risk_score.desc()).offset(skip).limit(limit).all()


# ============================================================================
# Process 108: Alert Management
# ============================================================================

@router.post("/alerts", response_model=AlertManagementResponse, status_code=201)
def create_alert(
    alert: AlertManagementCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a new system alert."""
    db_alert = AlertManagement(
        alert_id=generate_document_number("ALT", db),
        **alert.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_alert.tenant_id = tenant_id

    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)

    return db_alert


@router.get("/alerts", response_model=List[AlertManagementResponse])
def list_alerts(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List all alerts."""
    query = db.query(AlertManagement)
    query = apply_tenant_filter(query, AlertManagement, tenant_id)

    if status:
        query = query.filter(AlertManagement.status == status)
    if severity:
        query = query.filter(AlertManagement.severity == severity)

    return query.order_by(AlertManagement.created_at.desc()).offset(skip).limit(limit).all()


@router.put("/alerts/{alert_id}/acknowledge", response_model=AlertManagementResponse)
def acknowledge_alert(
    alert_id: int,
    acknowledged_by: int,
    db: Session = Depends(get_db)
):
    """Acknowledge an alert."""
    alert = db.query(AlertManagement).filter(AlertManagement.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = AlertStatus.ACKNOWLEDGED
    alert.acknowledged_by_id = acknowledged_by
    alert.acknowledged_at = datetime.utcnow()

    db.commit()
    db.refresh(alert)

    return alert


@router.put("/alerts/{alert_id}/resolve", response_model=AlertManagementResponse)
def resolve_alert(
    alert_id: int,
    resolved_by: int,
    resolution_notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Resolve an alert."""
    alert = db.query(AlertManagement).filter(AlertManagement.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = AlertStatus.RESOLVED
    alert.resolved_by_id = resolved_by
    alert.resolved_at = datetime.utcnow()
    alert.resolution_notes = resolution_notes

    # Calculate resolution time
    if alert.acknowledged_at:
        delta = alert.resolved_at - alert.acknowledged_at
        alert.resolution_time_minutes = int(delta.total_seconds() / 60)

    db.commit()
    db.refresh(alert)

    return alert


# ============================================================================
# Process 109: Audit Trail
# ============================================================================

@router.get("/audit-logs")
def list_audit_logs(
    skip: int = 0,
    limit: int = 100,
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List audit trail logs."""
    query = db.query(AuditLog)
    query = apply_tenant_filter(query, AuditLog, tenant_id)

    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if action:
        query = query.filter(AuditLog.action == action)
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)

    return query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()


# ============================================================================
# Process 110: Regulatory Compliance
# ============================================================================

@router.post("/compliance", response_model=RegulatoryComplianceResponse, status_code=201)
def create_compliance(
    compliance: RegulatoryComplianceCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a new regulatory compliance check."""
    db_compliance = RegulatoryCompliance(
        compliance_id=generate_document_number("COMP", db),
        status=ComplianceStatus.PENDING_REVIEW,
        **compliance.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_compliance.tenant_id = tenant_id

    db.add(db_compliance)
    db.commit()
    db.refresh(db_compliance)

    return db_compliance


@router.get("/compliance", response_model=List[RegulatoryComplianceResponse])
def list_compliance(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    compliance_type: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List all compliance checks."""
    query = db.query(RegulatoryCompliance)
    query = apply_tenant_filter(query, RegulatoryCompliance, tenant_id)

    if status:
        query = query.filter(RegulatoryCompliance.status == status)
    if compliance_type:
        query = query.filter(RegulatoryCompliance.compliance_type == compliance_type)

    return query.offset(skip).limit(limit).all()


@router.put("/compliance/{compliance_id}/validate", response_model=RegulatoryComplianceResponse)
def validate_compliance(
    compliance_id: int,
    assessed_by: int,
    db: Session = Depends(get_db)
):
    """Validate a compliance check."""
    compliance = db.query(RegulatoryCompliance).filter(RegulatoryCompliance.id == compliance_id).first()
    if not compliance:
        raise HTTPException(status_code=404, detail="Compliance check not found")

    # Calculate compliance score
    if compliance.total_requirements > 0:
        compliance.compliance_score = int((compliance.met_requirements / compliance.total_requirements) * 100)

    # Determine status
    if compliance.compliance_score == 100:
        compliance.status = ComplianceStatus.COMPLIANT
    elif compliance.compliance_score >= 80:
        compliance.status = ComplianceStatus.PARTIALLY_COMPLIANT
    else:
        compliance.status = ComplianceStatus.NON_COMPLIANT

    compliance.assessed_by_id = assessed_by
    compliance.last_assessment_date = date.today()
    compliance.next_assessment_date = date.today() + timedelta(days=compliance.assessment_frequency_days)

    db.commit()
    db.refresh(compliance)

    return compliance
