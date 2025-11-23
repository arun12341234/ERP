"""
Lead management endpoints with qualification and assignment workflows.
Processes: Lead Capture, Qualification, Assignment
"""
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.core.config import settings
from app.models.user import User
from app.models.lead import Lead, LeadStatus
from app.schemas.lead import Lead as LeadSchema, LeadCreate, LeadUpdate

router = APIRouter(prefix="/leads", tags=["leads"])


def apply_tenant_filter(query, user: User):
    if settings.ENABLE_TENANCY and hasattr(user, "tenant_id"):
        query = query.filter(Lead.tenant_id == user.tenant_id)
    return query


@router.get("", response_model=List[LeadSchema])
def list_leads(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all leads with optional status filter."""
    query = db.query(Lead)
    query = apply_tenant_filter(query, current_user)

    if status:
        query = query.filter(Lead.status == status)

    leads = query.offset(skip).limit(limit).all()
    return leads


@router.post("", response_model=LeadSchema, status_code=status.HTTP_201_CREATED)
def create_lead(
    lead_in: LeadCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 1: Lead Capture - Create a new lead."""
    lead_data = lead_in.model_dump()

    if settings.ENABLE_TENANCY and hasattr(current_user, "tenant_id"):
        lead_data["tenant_id"] = current_user.tenant_id

    db_lead = Lead(**lead_data)
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead


@router.get("/{lead_id}", response_model=LeadSchema)
def get_lead(
    lead_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get lead by ID."""
    query = db.query(Lead).filter(Lead.id == lead_id)
    query = apply_tenant_filter(query, current_user)
    lead = query.first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.put("/{lead_id}", response_model=LeadSchema)
def update_lead(
    lead_id: int,
    lead_update: LeadUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a lead."""
    query = db.query(Lead).filter(Lead.id == lead_id)
    query = apply_tenant_filter(query, current_user)
    lead = query.first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    update_data = lead_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)

    db.commit()
    db.refresh(lead)
    return lead


@router.post("/{lead_id}/qualify", response_model=LeadSchema)
def qualify_lead(
    lead_id: int,
    score: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 2: Lead Qualification - Score and classify lead."""
    query = db.query(Lead).filter(Lead.id == lead_id)
    query = apply_tenant_filter(query, current_user)
    lead = query.first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead.score = max(0, min(100, score))  # Ensure 0-100

    # Auto-classify based on score
    if lead.score >= 70:
        lead.status = LeadStatus.QUALIFIED
        lead.qualified_at = datetime.utcnow()
    elif lead.score < 30:
        lead.status = LeadStatus.REJECTED
    else:
        lead.status = LeadStatus.CONTACTED

    db.commit()
    db.refresh(lead)
    return lead


@router.post("/{lead_id}/assign", response_model=LeadSchema)
def assign_lead(
    lead_id: int,
    assigned_to_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 3: Lead Assignment - Assign lead to user."""
    query = db.query(Lead).filter(Lead.id == lead_id)
    query = apply_tenant_filter(query, current_user)
    lead = query.first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Verify assignee exists
    assignee = db.query(User).filter(User.id == assigned_to_id).first()
    if not assignee:
        raise HTTPException(status_code=404, detail="Assignee not found")

    lead.assigned_to_id = assigned_to_id
    db.commit()
    db.refresh(lead)
    return lead


@router.post("/{lead_id}/convert", response_model=LeadSchema)
def convert_lead(
    lead_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Convert qualified lead to customer (marks as converted)."""
    query = db.query(Lead).filter(Lead.id == lead_id)
    query = apply_tenant_filter(query, current_user)
    lead = query.first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if lead.status != LeadStatus.QUALIFIED:
        raise HTTPException(status_code=400, detail="Only qualified leads can be converted")

    lead.status = LeadStatus.CONVERTED
    lead.converted_at = datetime.utcnow()

    db.commit()
    db.refresh(lead)
    return lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(
    lead_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a lead."""
    query = db.query(Lead).filter(Lead.id == lead_id)
    query = apply_tenant_filter(query, current_user)
    lead = query.first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    db.delete(lead)
    db.commit()
    return None
