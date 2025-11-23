"""
Consolidated CRM router - Customers, Opportunities, Quotes, Sales Orders.
Implements the 15 CRM business processes.
"""
from typing import List
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.core.config import settings
from app.models.user import User
from app.models.customer import Customer, CustomerStatus
from app.models.opportunity import Opportunity, OpportunityStage
from app.models.quote import Quote, QuoteStatus
from app.models.sales_order import SalesOrder, SalesOrderStatus
from app.models.feedback import Feedback
from app.models.support_ticket import SupportTicket
from app.models.contract import Contract, ContractStatus
from app.schemas import (
    Customer as CustomerSchema, CustomerCreate, CustomerUpdate,
    Opportunity as OpportunitySchema, OpportunityCreate, OpportunityUpdate,
    Quote as QuoteSchema, QuoteCreate, QuoteUpdate,
    SalesOrder as SalesOrderSchema, SalesOrderCreate, SalesOrderUpdate,
    Feedback as FeedbackSchema, FeedbackCreate, FeedbackUpdate,
    SupportTicket as SupportTicketSchema, SupportTicketCreate, SupportTicketUpdate,
    Contract as ContractSchema, ContractCreate, ContractUpdate,
)

router = APIRouter(tags=["crm"])


def apply_tenant_filter(query, model, user: User):
    if settings.ENABLE_TENANCY and hasattr(user, "tenant_id"):
        query = query.filter(getattr(model, "tenant_id") == user.tenant_id)
    return query


# ============= CUSTOMERS =============

@router.get("/customers", response_model=List[CustomerSchema])
def list_customers(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all customers."""
    query = db.query(Customer)
    query = apply_tenant_filter(query, Customer, current_user)
    return query.offset(skip).limit(limit).all()


@router.post("/customers", response_model=CustomerSchema, status_code=201)
def create_customer(
    customer_in: CustomerCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 4: Customer Registration - Create new customer account."""
    customer_data = customer_in.model_dump()

    if settings.ENABLE_TENANCY and hasattr(current_user, "tenant_id"):
        customer_data["tenant_id"] = current_user.tenant_id

    db_customer = Customer(**customer_data)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


@router.get("/customers/{customer_id}", response_model=CustomerSchema)
def get_customer(
    customer_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(Customer).filter(Customer.id == customer_id)
    query = apply_tenant_filter(query, Customer, current_user)
    customer = query.first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/customers/{customer_id}", response_model=CustomerSchema)
def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(Customer).filter(Customer.id == customer_id)
    query = apply_tenant_filter(query, Customer, current_user)
    customer = query.first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    for field, value in customer_update.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)
    return customer


# ============= OPPORTUNITIES =============

@router.get("/opportunities", response_model=List[OpportunitySchema])
def list_opportunities(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(Opportunity)
    query = apply_tenant_filter(query, Opportunity, current_user)
    return query.offset(skip).limit(limit).all()


@router.post("/opportunities", response_model=OpportunitySchema, status_code=201)
def create_opportunity(
    opp_in: OpportunityCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 5: Opportunity Creation - Create sales opportunity from lead."""
    opp_data = opp_in.model_dump()

    if settings.ENABLE_TENANCY and hasattr(current_user, "tenant_id"):
        opp_data["tenant_id"] = current_user.tenant_id

    # Calculate initial score based on amount
    if opp_data.get("amount", 0) > 10000:
        opp_data["score"] = min(100, int(opp_data["amount"] / 1000))

    db_opp = Opportunity(**opp_data)
    db.add(db_opp)
    db.commit()
    db.refresh(db_opp)
    return db_opp


# ============= QUOTES =============

@router.get("/quotes", response_model=List[QuoteSchema])
def list_quotes(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(Quote)
    query = apply_tenant_filter(query, Quote, current_user)
    return query.offset(skip).limit(limit).all()


@router.post("/quotes", response_model=QuoteSchema, status_code=201)
def create_quote(
    quote_in: QuoteCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 6: Quotation Request - Create price quote for customer."""
    quote_data = quote_in.model_dump()
    quote_data["created_by_id"] = current_user.id

    # Auto-generate quote number
    count = db.query(Quote).count()
    quote_data["quote_number"] = f"Q-{datetime.now().year}-{count + 1:05d}"

    if settings.ENABLE_TENANCY and hasattr(current_user, "tenant_id"):
        quote_data["tenant_id"] = current_user.tenant_id

    db_quote = Quote(**quote_data)
    db.add(db_quote)
    db.commit()
    db.refresh(db_quote)
    return db_quote


@router.post("/quotes/{quote_id}/approve", response_model=QuoteSchema)
def approve_quote(
    quote_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 7: Quote Approval - Review and authorize quote."""
    query = db.query(Quote).filter(Quote.id == quote_id)
    query = apply_tenant_filter(query, Quote, current_user)
    quote = query.first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can approve quotes")

    quote.status = QuoteStatus.APPROVED
    quote.approved_by_id = current_user.id
    quote.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(quote)
    return quote


# ============= SALES ORDERS =============

@router.get("/sales-orders", response_model=List[SalesOrderSchema])
def list_sales_orders(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(SalesOrder)
    query = apply_tenant_filter(query, SalesOrder, current_user)
    return query.offset(skip).limit(limit).all()


@router.post("/sales-orders", response_model=SalesOrderSchema, status_code=201)
def create_sales_order(
    order_in: SalesOrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 8: Sales Order Creation - Convert quote to order."""
    order_data = order_in.model_dump()
    order_data["created_by_id"] = current_user.id

    # Auto-generate order number
    count = db.query(SalesOrder).count()
    order_data["order_number"] = f"SO-{datetime.now().year}-{count + 1:05d}"

    if settings.ENABLE_TENANCY and hasattr(current_user, "tenant_id"):
        order_data["tenant_id"] = current_user.tenant_id

    db_order = SalesOrder(**order_data)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@router.post("/sales-orders/{order_id}/credit-check", response_model=SalesOrderSchema)
def perform_credit_check(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 9: Credit Check - Evaluate customer credit risk."""
    query = db.query(SalesOrder).filter(SalesOrder.id == order_id)
    query = apply_tenant_filter(query, SalesOrder, current_user)
    order = query.first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Get customer
    customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Simple credit check logic
    available_credit = customer.credit_limit - customer.current_balance

    if order.total_amount <= available_credit:
        order.credit_check_status = "approved"
        order.status = SalesOrderStatus.CREDIT_APPROVED
        order.credit_check_notes = f"Approved. Available credit: {available_credit}"
    else:
        order.credit_check_status = "rejected"
        order.status = SalesOrderStatus.CREDIT_REJECTED
        order.credit_check_notes = f"Insufficient credit. Needs: {order.total_amount}, Available: {available_credit}"

    db.commit()
    db.refresh(order)
    return order


@router.post("/sales-orders/{order_id}/confirm", response_model=SalesOrderSchema)
def confirm_sales_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 10: Order Confirmation - Check inventory and confirm."""
    query = db.query(SalesOrder).filter(SalesOrder.id == order_id)
    query = apply_tenant_filter(query, SalesOrder, current_user)
    order = query.first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.credit_check_status != "approved":
        raise HTTPException(status_code=400, detail="Credit check must be approved first")

    order.status = SalesOrderStatus.CONFIRMED
    order.confirmed_at = datetime.utcnow()

    db.commit()
    db.refresh(order)
    return order


# ============= FEEDBACK =============

@router.get("/feedback", response_model=List[FeedbackSchema])
def list_feedback(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(Feedback)
    query = apply_tenant_filter(query, Feedback, current_user)
    return query.offset(skip).limit(limit).all()


@router.post("/feedback", response_model=FeedbackSchema, status_code=201)
def create_feedback(
    feedback_in: FeedbackCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 11: Customer Feedback Logging - Capture and categorize."""
    feedback_data = feedback_in.model_dump()

    if settings.ENABLE_TENANCY and hasattr(current_user, "tenant_id"):
        feedback_data["tenant_id"] = current_user.tenant_id

    db_feedback = Feedback(**feedback_data)
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


# ============= SUPPORT TICKETS =============

@router.get("/tickets", response_model=List[SupportTicketSchema])
def list_tickets(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(SupportTicket)
    query = apply_tenant_filter(query, SupportTicket, current_user)
    return query.offset(skip).limit(limit).all()


@router.post("/tickets", response_model=SupportTicketSchema, status_code=201)
def create_ticket(
    ticket_in: SupportTicketCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 12: Support Ticket Creation - Log and assign issue."""
    ticket_data = ticket_in.model_dump()

    # Auto-generate ticket number
    count = db.query(SupportTicket).count()
    ticket_data["ticket_number"] = f"T-{datetime.now().year}-{count + 1:05d}"

    if settings.ENABLE_TENANCY and hasattr(current_user, "tenant_id"):
        ticket_data["tenant_id"] = current_user.tenant_id

    db_ticket = SupportTicket(**ticket_data)
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


@router.post("/tickets/{ticket_id}/resolve", response_model=SupportTicketSchema)
def resolve_ticket(
    ticket_id: int,
    resolution_notes: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 13: Ticket Resolution - Troubleshoot and close."""
    query = db.query(SupportTicket).filter(SupportTicket.id == ticket_id)
    query = apply_tenant_filter(query, SupportTicket, current_user)
    ticket = query.first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.resolution_notes = resolution_notes
    ticket.resolved_by_id = current_user.id
    ticket.status = "resolved"
    ticket.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(ticket)
    return ticket


@router.post("/tickets/{ticket_id}/escalate", response_model=SupportTicketSchema)
def escalate_ticket(
    ticket_id: int,
    escalate_to_id: int,
    reason: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 14: Complaint Escalation - Review and escalate."""
    query = db.query(SupportTicket).filter(SupportTicket.id == ticket_id)
    query = apply_tenant_filter(query, SupportTicket, current_user)
    ticket = query.first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.is_escalated = True
    ticket.escalated_to_id = escalate_to_id
    ticket.escalation_reason = reason
    ticket.status = "escalated"
    ticket.escalated_at = datetime.utcnow()

    db.commit()
    db.refresh(ticket)
    return ticket


# ============= CONTRACTS =============

@router.get("/contracts", response_model=List[ContractSchema])
def list_contracts(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(Contract)
    query = apply_tenant_filter(query, Contract, current_user)
    return query.offset(skip).limit(limit).all()


@router.post("/contracts", response_model=ContractSchema, status_code=201)
def create_contract(
    contract_in: ContractCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new customer contract."""
    contract_data = contract_in.model_dump()
    contract_data["created_by_id"] = current_user.id

    # Auto-generate contract number
    count = db.query(Contract).count()
    contract_data["contract_number"] = f"C-{datetime.now().year}-{count + 1:05d}"

    if settings.ENABLE_TENANCY and hasattr(current_user, "tenant_id"):
        contract_data["tenant_id"] = current_user.tenant_id

    db_contract = Contract(**contract_data)
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract


@router.post("/contracts/{contract_id}/renew", response_model=ContractSchema)
def renew_contract(
    contract_id: int,
    new_end_date: date,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process 15: Customer Contract Renewal - Notify and renew."""
    query = db.query(Contract).filter(Contract.id == contract_id)
    query = apply_tenant_filter(query, Contract, current_user)
    contract = query.first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    contract.status = ContractStatus.RENEWED
    contract.end_date = new_end_date
    contract.renewal_date = datetime.now().date()
    contract.renewed_at = datetime.utcnow()
    contract.renewal_notified = False  # Reset for next renewal cycle

    db.commit()
    db.refresh(contract)
    return contract


@router.get("/contracts/expiring", response_model=List[ContractSchema])
def get_expiring_contracts(
    days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get contracts expiring within specified days."""
    expiry_date = date.today() + timedelta(days=days)

    query = db.query(Contract).filter(
        Contract.status == ContractStatus.ACTIVE,
        Contract.end_date <= expiry_date,
        Contract.end_date >= date.today()
    )
    query = apply_tenant_filter(query, Contract, current_user)

    return query.all()
