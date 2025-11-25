"""
Pydantic schemas for Governance, Audit, AI & System Ops module.
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


# ============================================================================
# Process 101: Role & Access Assignment
# ============================================================================

class RoleAssignmentCreate(BaseModel):
    user_id: int
    role_type: str
    role_name: str
    role_description: Optional[str] = None
    permissions: str  # JSON object
    access_modules: Optional[str] = None  # JSON array
    expires_at: Optional[datetime] = None


class RoleAssignmentResponse(BaseModel):
    id: int
    assignment_id: str
    user_id: int
    role_type: str
    role_name: str
    role_description: Optional[str]
    permissions: str
    access_modules: Optional[str]
    status: str
    assigned_by_id: Optional[int]
    assigned_at: datetime
    expires_at: Optional[datetime]
    revoked_by_id: Optional[int]
    revoked_at: Optional[datetime]
    revocation_reason: Optional[str]
    ip_restrictions: Optional[str]
    time_restrictions: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 102: Data Backup
# ============================================================================

class DataBackupCreate(BaseModel):
    backup_type: str  # full, incremental, differential
    backup_name: str
    description: Optional[str] = None
    scheduled_at: datetime
    storage_type: str  # local, s3, azure, gcs
    database_name: Optional[str] = None
    retention_days: int = 30


class DataBackupResponse(BaseModel):
    id: int
    backup_id: str
    backup_type: str
    backup_name: str
    description: Optional[str]
    status: str
    scheduled_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    storage_type: str
    storage_path: Optional[str]
    backup_file_name: Optional[str]
    backup_size_mb: float
    compressed_size_mb: float
    compression_ratio: float
    duration_seconds: int
    database_name: Optional[str]
    tables_included: Optional[str]
    exclude_tables: Optional[str]
    is_encrypted: int
    encryption_algorithm: Optional[str]
    is_verified: int
    checksum: Optional[str]
    error_message: Optional[str]
    retry_count: int
    retention_days: int
    expires_at: Optional[datetime]
    is_deleted: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 103: System Health Monitoring
# ============================================================================

class SystemHealthCheckCreate(BaseModel):
    component_type: str  # api, database, cache, queue, storage
    component_name: str
    component_url: Optional[str] = None
    check_interval_seconds: int = 60


class SystemHealthCheckResponse(BaseModel):
    id: int
    check_id: str
    component_type: str
    component_name: str
    component_url: Optional[str]
    status: str
    previous_status: Optional[str]
    response_time_ms: Optional[int]
    cpu_usage_percent: Optional[float]
    memory_usage_percent: Optional[float]
    disk_usage_percent: Optional[float]
    uptime_seconds: Optional[int]
    downtime_seconds: int
    availability_percent: float
    error_count: int
    last_error_message: Optional[str]
    last_error_at: Optional[datetime]
    is_alert_sent: int
    alert_sent_at: Optional[datetime]
    escalated_to: Optional[str]
    response_time_threshold_ms: int
    cpu_threshold_percent: float
    memory_threshold_percent: float
    check_interval_seconds: int
    last_checked_at: Optional[datetime]
    next_check_at: Optional[datetime]
    health_metadata: Optional[str]
    logs: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 104: API Integration
# ============================================================================

class APIIntegrationCreate(BaseModel):
    integration_name: str
    provider_name: str
    description: Optional[str] = None
    base_url: str
    auth_type: str  # api_key, oauth2, basic_auth, jwt, bearer_token
    api_key: Optional[str] = None
    timeout_seconds: int = 30


class APIIntegrationResponse(BaseModel):
    id: int
    integration_id: str
    integration_name: str
    provider_name: str
    description: Optional[str]
    base_url: str
    api_version: Optional[str]
    documentation_url: Optional[str]
    auth_type: str
    token_expires_at: Optional[datetime]
    custom_headers: Optional[str]
    status: str
    is_active: int
    rate_limit_requests: Optional[int]
    rate_limit_period_seconds: int
    current_usage: int
    last_test_at: Optional[datetime]
    last_test_status: Optional[str]
    deployed_at: Optional[datetime]
    deployed_by_id: Optional[int]
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time_ms: int
    last_request_at: Optional[datetime]
    last_error_message: Optional[str]
    last_error_at: Optional[datetime]
    consecutive_failures: int
    webhook_url: Optional[str]
    timeout_seconds: int
    retry_count: int
    retry_delay_seconds: int
    tags: Optional[str]
    integration_metadata: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 105: Document Digitization
# ============================================================================

class DocumentDigitizationCreate(BaseModel):
    document_type: str
    document_name: str
    description: Optional[str] = None
    original_filename: str
    file_path: str
    file_size_bytes: int
    ocr_language: str = "eng"


class DocumentDigitizationResponse(BaseModel):
    id: int
    document_id: str
    document_type: str
    document_name: str
    description: Optional[str]
    original_filename: str
    file_path: str
    file_size_bytes: int
    file_format: Optional[str]
    status: str
    ocr_engine: Optional[str]
    ocr_language: str
    ocr_confidence: Optional[float]
    extracted_text: Optional[str]
    extracted_data: Optional[str]
    entities_detected: Optional[str]
    classification_confidence: Optional[float]
    suggested_document_type: Optional[str]
    processing_started_at: Optional[datetime]
    processing_completed_at: Optional[datetime]
    processing_duration_ms: int
    page_count: int
    pages_processed: int
    reference_type: Optional[str]
    reference_id: Optional[int]
    is_verified: int
    verified_by_id: Optional[int]
    verified_at: Optional[datetime]
    verification_notes: Optional[str]
    error_message: Optional[str]
    retry_count: int
    uploaded_by_id: Optional[int]
    tags: Optional[str]
    document_metadata: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 106: Analytics Dashboard
# ============================================================================

class AnalyticsDashboardCreate(BaseModel):
    dashboard_name: str
    dashboard_type: str  # executive, sales, finance, operations
    description: Optional[str] = None
    layout_config: str  # JSON object
    widgets: str  # JSON array
    refresh_frequency: str = "every_hour"


class AnalyticsDashboardResponse(BaseModel):
    id: int
    dashboard_id: str
    dashboard_name: str
    dashboard_type: str
    description: Optional[str]
    layout_config: str
    widgets: str
    data_sources: Optional[str]
    refresh_frequency: str
    last_refreshed_at: Optional[datetime]
    next_refresh_at: Optional[datetime]
    is_public: int
    owner_id: Optional[int]
    shared_with: Optional[str]
    is_active: int
    is_published: int
    default_filters: Optional[str]
    date_range: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KPIMetricCreate(BaseModel):
    metric_name: str
    metric_category: Optional[str] = None
    description: Optional[str] = None
    current_value: float
    target_value: Optional[float] = None
    period_start: date
    period_end: date


class KPIMetricResponse(BaseModel):
    id: int
    metric_id: str
    metric_name: str
    metric_category: Optional[str]
    description: Optional[str]
    current_value: float
    previous_value: Optional[float]
    target_value: Optional[float]
    change_value: float
    change_percentage: float
    is_improvement: Optional[int]
    period_start: date
    period_end: date
    comparison_period_start: Optional[date]
    comparison_period_end: Optional[date]
    visualization_type: Optional[str]
    chart_data: Optional[str]
    data_source_query: Optional[str]
    calculation_formula: Optional[str]
    warning_threshold: Optional[float]
    critical_threshold: Optional[float]
    is_threshold_breached: int
    unit: Optional[str]
    decimal_places: int
    prefix: Optional[str]
    suffix: Optional[str]
    calculated_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 107: Risk Assessment
# ============================================================================

class RiskAssessmentCreate(BaseModel):
    risk_title: str
    risk_category: str
    description: str
    likelihood_score: int  # 1-5
    impact_score: int  # 1-5
    identified_date: date


class RiskAssessmentResponse(BaseModel):
    id: int
    risk_id: str
    risk_title: str
    risk_category: str
    description: str
    likelihood_score: int
    impact_score: int
    risk_score: int
    risk_level: str
    status: str
    financial_impact: int
    operational_impact: Optional[str]
    affected_processes: Optional[str]
    identified_date: date
    target_resolution_date: Optional[date]
    actual_resolution_date: Optional[date]
    risk_owner_id: Optional[int]
    identified_by_id: Optional[int]
    mitigation_strategy: Optional[str]
    mitigation_actions: Optional[str]
    mitigation_cost: int
    mitigation_status: Optional[str]
    existing_controls: Optional[str]
    proposed_controls: Optional[str]
    control_effectiveness: Optional[str]
    residual_likelihood_score: Optional[int]
    residual_impact_score: Optional[int]
    residual_risk_score: Optional[int]
    residual_risk_level: Optional[str]
    last_reviewed_at: Optional[date]
    next_review_date: Optional[date]
    review_frequency_days: int
    is_escalated: int
    escalated_to_id: Optional[int]
    escalation_date: Optional[datetime]
    notes: Optional[str]
    lessons_learned: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 108: Alert Management
# ============================================================================

class AlertManagementCreate(BaseModel):
    alert_type: str  # system, security, performance, business
    severity: str  # info, warning, error, critical
    title: str
    message: str
    source_system: Optional[str] = None
    source_component: Optional[str] = None


class AlertManagementResponse(BaseModel):
    id: int
    alert_id: str
    alert_type: str
    severity: str
    title: str
    message: str
    source_system: Optional[str]
    source_component: Optional[str]
    source_entity_type: Optional[str]
    source_entity_id: Optional[int]
    status: str
    rule_id: Optional[str]
    rule_name: Optional[str]
    rule_condition: Optional[str]
    metric_name: Optional[str]
    threshold_value: Optional[str]
    actual_value: Optional[str]
    assigned_to_id: Optional[int]
    assigned_at: Optional[datetime]
    acknowledged_by_id: Optional[int]
    acknowledged_at: Optional[datetime]
    resolved_by_id: Optional[int]
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]
    resolution_time_minutes: Optional[int]
    notification_channels: Optional[str]
    notification_sent_at: Optional[datetime]
    notification_recipients: Optional[str]
    is_escalated: int
    escalation_level: int
    escalated_to_id: Optional[int]
    escalated_at: Optional[datetime]
    is_auto_resolvable: int
    auto_resolved: int
    parent_alert_id: Optional[str]
    related_alert_ids: Optional[str]
    occurrence_count: int
    first_occurred_at: datetime
    last_occurred_at: datetime
    priority: int
    context_data: Optional[str]
    error_stack_trace: Optional[str]
    tags: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 110: Regulatory Compliance
# ============================================================================

class RegulatoryComplianceCreate(BaseModel):
    compliance_type: str  # gdpr, sox, hipaa, pci_dss, etc.
    regulation_name: str
    regulation_code: Optional[str] = None
    description: Optional[str] = None
    checklist: str  # JSON array
    assessment_frequency_days: int = 365


class RegulatoryComplianceResponse(BaseModel):
    id: int
    compliance_id: str
    compliance_type: str
    regulation_name: str
    regulation_code: Optional[str]
    description: Optional[str]
    status: str
    compliance_score: int
    total_requirements: int
    met_requirements: int
    pending_requirements: int
    failed_requirements: int
    checklist: str
    last_assessment_date: Optional[date]
    next_assessment_date: Optional[date]
    assessment_frequency_days: int
    assessed_by_id: Optional[int]
    assessor_name: Optional[str]
    assessor_organization: Optional[str]
    evidence_documents: Optional[str]
    supporting_documentation: Optional[str]
    remediation_plan: Optional[str]
    remediation_deadline: Optional[date]
    remediation_owner_id: Optional[int]
    remediation_status: Optional[str]
    identified_gaps: Optional[str]
    gap_analysis_notes: Optional[str]
    non_compliance_risk: Optional[str]
    potential_penalties: int
    is_certified: int
    certification_number: Optional[str]
    certification_date: Optional[date]
    certification_expiry: Optional[date]
    certification_body: Optional[str]
    monitoring_enabled: int
    last_monitored_at: Optional[datetime]
    reporting_frequency: Optional[str]
    last_report_date: Optional[date]
    next_report_due: Optional[date]
    compliance_officer_id: Optional[int]
    department: Optional[str]
    notes: Optional[str]
    auditor_comments: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
