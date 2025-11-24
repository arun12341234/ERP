"""
Finance router - Finance, Accounting & Compliance (processes 46-60).
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models import (
    ChartOfAccounts, Invoice, Expense, VendorPayment, CustomerReceipt,
    JournalEntry, JournalEntryLine, BankReconciliation, BankReconciliationLine,
    FixedAsset, Depreciation, TaxFiling, Budget, BudgetLine,
    CostCenter, FinancialPeriod, CashFlow, CashFlowLine, AuditLog
)
from app.schemas.finance import (
    ChartOfAccountsCreate, ChartOfAccountsResponse,
    InvoiceCreate, InvoiceResponse,
    ExpenseCreate, ExpenseResponse,
    VendorPaymentCreate, VendorPaymentResponse,
    CustomerReceiptCreate, CustomerReceiptResponse,
    JournalEntryCreate, JournalEntryResponse,
    BankReconciliationCreate, BankReconciliationResponse,
    FixedAssetCreate, FixedAssetResponse,
    DepreciationCreate, DepreciationResponse,
    TaxFilingCreate, TaxFilingResponse,
    BudgetCreate, BudgetResponse,
    CostCenterCreate, CostCenterResponse,
    FinancialPeriodCreate, FinancialPeriodResponse,
    CashFlowCreate, CashFlowResponse,
    AuditLogCreate, AuditLogResponse,
)

router = APIRouter(tags=["finance"])


def apply_tenant_filter(query, model, tenant_id: Optional[int] = None):
    """Apply tenant filter if multi-tenancy is enabled."""
    if settings.ENABLE_TENANCY and tenant_id is not None:
        return query.filter(model.tenant_id == tenant_id)
    return query


def create_audit_log(db: Session, user_id: Optional[int], action: str, entity_type: str,
                     entity_id: Optional[int], description: str, tenant_id: Optional[int] = None):
    """Helper to create audit log entries."""
    audit = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(audit)


# ============================================================================
# Process 46: Chart of Accounts Setup
# ============================================================================

@router.post("/chart-of-accounts", response_model=ChartOfAccountsResponse)
def create_account(
    account: ChartOfAccountsCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """
    Process 46: Chart of Accounts Setup
    Input: Finance data → Create ledgers
    Output: COA
    """
    # Check for duplicate account code
    existing = db.query(ChartOfAccounts).filter(
        ChartOfAccounts.account_code == account.account_code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Account code already exists")

    db_account = ChartOfAccounts(
        account_code=account.account_code,
        account_name=account.account_name,
        account_type=account.account_type,
        account_subtype=account.account_subtype,
        parent_account_id=account.parent_account_id,
        level=account.level,
        is_control_account=account.is_control_account,
        allow_posting=account.allow_posting,
        opening_balance=account.opening_balance,
        current_balance=account.opening_balance,
        description=account.description,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)

    create_audit_log(db, user_id, "create", "ChartOfAccounts", db_account.id,
                    f"Created account {account.account_code}", tenant_id)
    db.commit()

    return db_account


@router.get("/chart-of-accounts", response_model=List[ChartOfAccountsResponse])
def list_accounts(
    account_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List chart of accounts."""
    query = db.query(ChartOfAccounts)
    query = apply_tenant_filter(query, ChartOfAccounts, tenant_id)

    if account_type:
        query = query.filter(ChartOfAccounts.account_type == account_type)
    if is_active is not None:
        query = query.filter(ChartOfAccounts.is_active == is_active)

    return query.order_by(ChartOfAccounts.account_code).all()


# ============================================================================
# Process 47: Invoice Creation
# ============================================================================

@router.post("/invoices", response_model=InvoiceResponse)
def create_invoice(
    invoice: InvoiceCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """
    Process 47: Invoice Creation
    Input: Sales order → Generate bill
    Output: Customer invoice
    """
    # Generate invoice number
    count = db.query(Invoice).count()
    invoice_number = f"INV-{datetime.now().year}-{count + 1:05d}"

    # Calculate amount due
    amount_due = invoice.total_amount

    db_invoice = Invoice(
        invoice_number=invoice_number,
        customer_id=invoice.customer_id,
        sales_order_id=invoice.sales_order_id,
        invoice_date=invoice.invoice_date,
        due_date=invoice.due_date,
        payment_terms=invoice.payment_terms,
        subtotal=invoice.subtotal,
        tax_amount=invoice.tax_amount,
        discount_amount=invoice.discount_amount,
        total_amount=invoice.total_amount,
        amount_due=amount_due,
        notes=invoice.notes,
        terms_conditions=invoice.terms_conditions,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)

    create_audit_log(db, user_id, "create", "Invoice", db_invoice.id,
                    f"Created invoice {invoice_number}", tenant_id)
    db.commit()

    return db_invoice


@router.get("/invoices", response_model=List[InvoiceResponse])
def list_invoices(
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List invoices."""
    query = db.query(Invoice)
    query = apply_tenant_filter(query, Invoice, tenant_id)

    if status:
        query = query.filter(Invoice.status == status)
    if customer_id:
        query = query.filter(Invoice.customer_id == customer_id)

    return query.order_by(Invoice.invoice_date.desc()).all()


@router.post("/invoices/{invoice_id}/send")
def send_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """Send invoice to customer."""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    invoice.status = "sent"
    db.commit()

    create_audit_log(db, user_id, "update", "Invoice", invoice.id,
                    f"Sent invoice {invoice.invoice_number}", tenant_id)
    db.commit()

    return {"message": "Invoice sent", "invoice_number": invoice.invoice_number}


# ============================================================================
# Process 48: Expense Booking
# ============================================================================

@router.post("/expenses", response_model=ExpenseResponse)
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """
    Process 48: Expense Booking
    Input: Expense bill → Validate & record
    Output: Expense entry
    """
    # Generate expense number
    count = db.query(Expense).count()
    expense_number = f"EXP-{datetime.now().year}-{count + 1:05d}"

    db_expense = Expense(
        expense_number=expense_number,
        expense_date=expense.expense_date,
        category=expense.category,
        description=expense.description,
        amount=expense.amount,
        tax_amount=expense.tax_amount,
        total_amount=expense.total_amount,
        vendor_id=expense.vendor_id,
        payee_name=expense.payee_name,
        account_id=expense.account_id,
        cost_center_id=expense.cost_center_id,
        notes=expense.notes,
        submitted_by_id=user_id,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)

    create_audit_log(db, user_id, "create", "Expense", db_expense.id,
                    f"Created expense {expense_number}", tenant_id)
    db.commit()

    return db_expense


@router.get("/expenses", response_model=List[ExpenseResponse])
def list_expenses(
    status: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List expenses."""
    query = db.query(Expense)
    query = apply_tenant_filter(query, Expense, tenant_id)

    if status:
        query = query.filter(Expense.status == status)
    if category:
        query = query.filter(Expense.category == category)

    return query.order_by(Expense.expense_date.desc()).all()


@router.post("/expenses/{expense_id}/approve")
def approve_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """Approve an expense."""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    expense.status = "approved"
    expense.approved_by_id = user_id
    expense.approval_date = datetime.utcnow()
    db.commit()

    create_audit_log(db, user_id, "approve", "Expense", expense.id,
                    f"Approved expense {expense.expense_number}", tenant_id)
    db.commit()

    return {"message": "Expense approved", "expense_number": expense.expense_number}


@router.post("/expenses/{expense_id}/post")
def post_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """Post expense to GL."""
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    if expense.status != "approved":
        raise HTTPException(status_code=400, detail="Expense must be approved first")

    expense.status = "posted"
    db.commit()

    create_audit_log(db, user_id, "post", "Expense", expense.id,
                    f"Posted expense {expense.expense_number}", tenant_id)
    db.commit()

    return {"message": "Expense posted", "expense_number": expense.expense_number}


# ============================================================================
# Process 49: Vendor Payment
# ============================================================================

@router.post("/vendor-payments", response_model=VendorPaymentResponse)
def create_vendor_payment(
    payment: VendorPaymentCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """
    Process 49: Vendor Payment
    Input: Payable due → Approve payment
    Output: Payment voucher
    """
    # Generate payment number
    count = db.query(VendorPayment).count()
    payment_number = f"VP-{datetime.now().year}-{count + 1:05d}"

    db_payment = VendorPayment(
        payment_number=payment_number,
        vendor_id=payment.vendor_id,
        payment_date=payment.payment_date,
        payment_method=payment.payment_method,
        reference_number=payment.reference_number,
        payment_amount=payment.payment_amount,
        bank_account_id=payment.bank_account_id,
        notes=payment.notes,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    create_audit_log(db, user_id, "create", "VendorPayment", db_payment.id,
                    f"Created vendor payment {payment_number}", tenant_id)
    db.commit()

    return db_payment


@router.get("/vendor-payments", response_model=List[VendorPaymentResponse])
def list_vendor_payments(
    status: Optional[str] = None,
    vendor_id: Optional[int] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List vendor payments."""
    query = db.query(VendorPayment)
    query = apply_tenant_filter(query, VendorPayment, tenant_id)

    if status:
        query = query.filter(VendorPayment.status == status)
    if vendor_id:
        query = query.filter(VendorPayment.vendor_id == vendor_id)

    return query.order_by(VendorPayment.payment_date.desc()).all()


@router.post("/vendor-payments/{payment_id}/approve")
def approve_vendor_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """Approve a vendor payment."""
    payment = db.query(VendorPayment).filter(VendorPayment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment.status = "approved"
    payment.approved_by_id = user_id
    payment.approval_date = datetime.utcnow()
    db.commit()

    create_audit_log(db, user_id, "approve", "VendorPayment", payment.id,
                    f"Approved payment {payment.payment_number}", tenant_id)
    db.commit()

    return {"message": "Payment approved", "payment_number": payment.payment_number}


@router.post("/vendor-payments/{payment_id}/process")
def process_vendor_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """Process a vendor payment."""
    payment = db.query(VendorPayment).filter(VendorPayment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.status != "approved":
        raise HTTPException(status_code=400, detail="Payment must be approved first")

    payment.status = "processed"
    payment.processed_by_id = user_id
    payment.processed_date = datetime.utcnow()
    db.commit()

    create_audit_log(db, user_id, "update", "VendorPayment", payment.id,
                    f"Processed payment {payment.payment_number}", tenant_id)
    db.commit()

    return {"message": "Payment processed", "payment_number": payment.payment_number}


# ============================================================================
# Process 50: Customer Receipt
# ============================================================================

@router.post("/customer-receipts", response_model=CustomerReceiptResponse)
def create_customer_receipt(
    receipt: CustomerReceiptCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """
    Process 50: Customer Receipt
    Input: Payment details → Record receipt
    Output: Receipt voucher
    """
    # Generate receipt number
    count = db.query(CustomerReceipt).count()
    receipt_number = f"CR-{datetime.now().year}-{count + 1:05d}"

    db_receipt = CustomerReceipt(
        receipt_number=receipt_number,
        customer_id=receipt.customer_id,
        invoice_id=receipt.invoice_id,
        receipt_date=receipt.receipt_date,
        receipt_method=receipt.receipt_method,
        reference_number=receipt.reference_number,
        receipt_amount=receipt.receipt_amount,
        bank_account_id=receipt.bank_account_id,
        notes=receipt.notes,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_receipt)
    db.commit()
    db.refresh(db_receipt)

    create_audit_log(db, user_id, "create", "CustomerReceipt", db_receipt.id,
                    f"Created customer receipt {receipt_number}", tenant_id)
    db.commit()

    return db_receipt


@router.get("/customer-receipts", response_model=List[CustomerReceiptResponse])
def list_customer_receipts(
    customer_id: Optional[int] = None,
    invoice_id: Optional[int] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List customer receipts."""
    query = db.query(CustomerReceipt)
    query = apply_tenant_filter(query, CustomerReceipt, tenant_id)

    if customer_id:
        query = query.filter(CustomerReceipt.customer_id == customer_id)
    if invoice_id:
        query = query.filter(CustomerReceipt.invoice_id == invoice_id)

    return query.order_by(CustomerReceipt.receipt_date.desc()).all()


@router.post("/customer-receipts/{receipt_id}/record")
def record_customer_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """Record a customer receipt."""
    receipt = db.query(CustomerReceipt).filter(CustomerReceipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    receipt.status = "recorded"
    receipt.recorded_by_id = user_id
    receipt.recorded_date = datetime.utcnow()

    # Update invoice if linked
    if receipt.invoice_id:
        invoice = db.query(Invoice).filter(Invoice.id == receipt.invoice_id).first()
        if invoice:
            invoice.amount_paid += receipt.receipt_amount
            invoice.amount_due = invoice.total_amount - invoice.amount_paid

            if invoice.amount_due <= 0:
                invoice.status = "paid"
            elif invoice.amount_paid > 0:
                invoice.status = "partially_paid"

    db.commit()

    create_audit_log(db, user_id, "update", "CustomerReceipt", receipt.id,
                    f"Recorded receipt {receipt.receipt_number}", tenant_id)
    db.commit()

    return {"message": "Receipt recorded", "receipt_number": receipt.receipt_number}


# ============================================================================
# Process 51: Journal Entry
# ============================================================================

@router.post("/journal-entries", response_model=JournalEntryResponse)
def create_journal_entry(
    entry: JournalEntryCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """
    Process 51: Journal Entry
    Input: Adjustment trial → Post entry
    Output: Journal
    """
    # Validate balanced entry
    total_debits = sum(line.debit_amount for line in entry.lines)
    total_credits = sum(line.credit_amount for line in entry.lines)

    if total_debits != total_credits:
        raise HTTPException(status_code=400, detail="Entry not balanced: debits must equal credits")

    # Generate entry number
    count = db.query(JournalEntry).count()
    entry_number = f"JE-{datetime.now().year}-{count + 1:05d}"

    db_entry = JournalEntry(
        entry_number=entry_number,
        entry_date=entry.entry_date,
        entry_type=entry.entry_type,
        description=entry.description,
        reference=entry.reference,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_entry)
    db.flush()

    # Add lines
    for line in entry.lines:
        db_line = JournalEntryLine(
            journal_entry_id=db_entry.id,
            account_id=line.account_id,
            debit_amount=line.debit_amount,
            credit_amount=line.credit_amount,
            description=line.description,
            cost_center_id=line.cost_center_id,
            tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
        )
        db.add(db_line)

    db.commit()
    db.refresh(db_entry)

    create_audit_log(db, user_id, "create", "JournalEntry", db_entry.id,
                    f"Created journal entry {entry_number}", tenant_id)
    db.commit()

    return db_entry


@router.get("/journal-entries", response_model=List[JournalEntryResponse])
def list_journal_entries(
    status: Optional[str] = None,
    entry_type: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List journal entries."""
    query = db.query(JournalEntry)
    query = apply_tenant_filter(query, JournalEntry, tenant_id)

    if status:
        query = query.filter(JournalEntry.status == status)
    if entry_type:
        query = query.filter(JournalEntry.entry_type == entry_type)

    return query.order_by(JournalEntry.entry_date.desc()).all()


@router.post("/journal-entries/{entry_id}/post")
def post_journal_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """Post a journal entry to GL."""
    entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")

    if entry.status == "posted":
        raise HTTPException(status_code=400, detail="Entry already posted")

    # Get lines and update account balances
    lines = db.query(JournalEntryLine).filter(
        JournalEntryLine.journal_entry_id == entry_id
    ).all()

    for line in lines:
        account = db.query(ChartOfAccounts).filter(ChartOfAccounts.id == line.account_id).first()
        if account:
            # Debit increases assets/expenses, decreases liabilities/equity/revenue
            # Credit increases liabilities/equity/revenue, decreases assets/expenses
            if account.account_type in ["asset", "expense"]:
                account.current_balance += (line.debit_amount - line.credit_amount)
            else:  # liability, equity, revenue
                account.current_balance += (line.credit_amount - line.debit_amount)

    entry.status = "posted"
    entry.posted_by_id = user_id
    entry.posted_date = datetime.utcnow()
    db.commit()

    create_audit_log(db, user_id, "post", "JournalEntry", entry.id,
                    f"Posted journal entry {entry.entry_number}", tenant_id)
    db.commit()

    return {"message": "Journal entry posted", "entry_number": entry.entry_number}


# ============================================================================
# Process 52: Bank Reconciliation
# ============================================================================

@router.post("/bank-reconciliations", response_model=BankReconciliationResponse)
def create_bank_reconciliation(
    recon: BankReconciliationCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """
    Process 52: Bank Reconciliation
    Input: Bank statement → Match entries
    Output: Reconciliation
    """
    # Generate reconciliation number
    count = db.query(BankReconciliation).count()
    recon_number = f"BR-{datetime.now().year}-{count + 1:05d}"

    # Calculate difference
    difference = recon.statement_balance - recon.book_balance

    db_recon = BankReconciliation(
        reconciliation_number=recon_number,
        bank_account_id=recon.bank_account_id,
        statement_date=recon.statement_date,
        reconciliation_date=recon.reconciliation_date,
        opening_balance=recon.opening_balance,
        closing_balance=recon.closing_balance,
        statement_balance=recon.statement_balance,
        book_balance=recon.book_balance,
        difference=difference,
        notes=recon.notes,
        reconciled_by_id=user_id,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_recon)
    db.flush()

    # Add lines if provided
    if recon.lines:
        for line in recon.lines:
            db_line = BankReconciliationLine(
                reconciliation_id=db_recon.id,
                transaction_date=line.transaction_date,
                description=line.description,
                reference=line.reference,
                amount=line.amount,
                is_matched=line.is_matched,
                matched_transaction_id=line.matched_transaction_id,
                tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
            )
            db.add(db_line)

    db.commit()
    db.refresh(db_recon)

    create_audit_log(db, user_id, "create", "BankReconciliation", db_recon.id,
                    f"Created bank reconciliation {recon_number}", tenant_id)
    db.commit()

    return db_recon


@router.get("/bank-reconciliations", response_model=List[BankReconciliationResponse])
def list_bank_reconciliations(
    bank_account_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List bank reconciliations."""
    query = db.query(BankReconciliation)
    query = apply_tenant_filter(query, BankReconciliation, tenant_id)

    if bank_account_id:
        query = query.filter(BankReconciliation.bank_account_id == bank_account_id)
    if status:
        query = query.filter(BankReconciliation.status == status)

    return query.order_by(BankReconciliation.reconciliation_date.desc()).all()


@router.post("/bank-reconciliations/{recon_id}/complete")
def complete_bank_reconciliation(
    recon_id: int,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """Complete a bank reconciliation."""
    recon = db.query(BankReconciliation).filter(BankReconciliation.id == recon_id).first()
    if not recon:
        raise HTTPException(status_code=404, detail="Reconciliation not found")

    recon.status = "completed"
    db.commit()

    create_audit_log(db, user_id, "update", "BankReconciliation", recon.id,
                    f"Completed reconciliation {recon.reconciliation_number}", tenant_id)
    db.commit()

    return {"message": "Reconciliation completed", "reconciliation_number": recon.reconciliation_number}


# ============================================================================
# Process 53: Fixed Asset Addition
# ============================================================================

@router.post("/fixed-assets", response_model=FixedAssetResponse)
def create_fixed_asset(
    asset: FixedAssetCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """
    Process 53: Fixed Asset Addition
    Input: Asset invoice → Register asset
    Output: Asset master
    """
    # Generate asset number
    count = db.query(FixedAsset).count()
    asset_number = f"FA-{datetime.now().year}-{count + 1:05d}"

    # Calculate net book value
    net_book_value = asset.acquisition_cost - asset.salvage_value

    db_asset = FixedAsset(
        asset_number=asset_number,
        asset_name=asset.asset_name,
        description=asset.description,
        category=asset.category,
        acquisition_date=asset.acquisition_date,
        acquisition_cost=asset.acquisition_cost,
        vendor_id=asset.vendor_id,
        location=asset.location,
        department=asset.department,
        custodian=asset.custodian,
        depreciation_method=asset.depreciation_method,
        useful_life_years=asset.useful_life_years,
        salvage_value=asset.salvage_value,
        net_book_value=net_book_value,
        asset_account_id=asset.asset_account_id,
        depreciation_account_id=asset.depreciation_account_id,
        accumulated_depreciation_account_id=asset.accumulated_depreciation_account_id,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)

    create_audit_log(db, user_id, "create", "FixedAsset", db_asset.id,
                    f"Created fixed asset {asset_number}", tenant_id)
    db.commit()

    return db_asset


@router.get("/fixed-assets", response_model=List[FixedAssetResponse])
def list_fixed_assets(
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List fixed assets."""
    query = db.query(FixedAsset)
    query = apply_tenant_filter(query, FixedAsset, tenant_id)

    if category:
        query = query.filter(FixedAsset.category == category)
    if status:
        query = query.filter(FixedAsset.status == status)

    return query.order_by(FixedAsset.asset_number).all()


# ============================================================================
# Process 54: Depreciation Run
# ============================================================================

@router.post("/depreciations/run")
def run_depreciation(
    period_start: str,
    period_end: str,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """
    Process 54: Depreciation Run
    Input: Asset life → Calculate
    Output: Depreciation entry
    """
    from datetime import datetime as dt
    from dateutil.relativedelta import relativedelta

    period_start_date = dt.strptime(period_start, "%Y-%m-%d").date()
    period_end_date = dt.strptime(period_end, "%Y-%m-%d").date()

    # Get all active assets
    assets_query = db.query(FixedAsset).filter(FixedAsset.status == "active")
    assets_query = apply_tenant_filter(assets_query, FixedAsset, tenant_id)
    assets = assets_query.all()

    created_depreciations = []

    for asset in assets:
        # Simple straight-line depreciation
        if asset.depreciation_method == "straight_line":
            annual_depreciation = (asset.acquisition_cost - asset.salvage_value) / asset.useful_life_years
            monthly_depreciation = int(annual_depreciation / 12)

            # Calculate months in period
            months = (period_end_date.year - period_start_date.year) * 12 + \
                    (period_end_date.month - period_start_date.month) + 1

            depreciation_amount = monthly_depreciation * months
            accumulated_depreciation = asset.accumulated_depreciation + depreciation_amount
            net_book_value = asset.acquisition_cost - accumulated_depreciation

            # Create depreciation entry
            count = db.query(Depreciation).count()
            depreciation_number = f"DEP-{datetime.now().year}-{count + 1:05d}"

            db_depreciation = Depreciation(
                depreciation_number=depreciation_number,
                asset_id=asset.id,
                period_start=period_start_date,
                period_end=period_end_date,
                depreciation_date=period_end_date,
                depreciation_amount=depreciation_amount,
                accumulated_depreciation=accumulated_depreciation,
                net_book_value=net_book_value,
                tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
            )
            db.add(db_depreciation)

            # Update asset
            asset.accumulated_depreciation = accumulated_depreciation
            asset.net_book_value = net_book_value

            if net_book_value <= asset.salvage_value:
                asset.status = "fully_depreciated"

            created_depreciations.append(depreciation_number)

    db.commit()

    create_audit_log(db, user_id, "create", "Depreciation", None,
                    f"Ran depreciation for {len(created_depreciations)} assets", tenant_id)
    db.commit()

    return {
        "message": f"Depreciation run completed for {len(created_depreciations)} assets",
        "depreciation_numbers": created_depreciations
    }


@router.get("/depreciations", response_model=List[DepreciationResponse])
def list_depreciations(
    asset_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List depreciations."""
    query = db.query(Depreciation)
    query = apply_tenant_filter(query, Depreciation, tenant_id)

    if asset_id:
        query = query.filter(Depreciation.asset_id == asset_id)
    if status:
        query = query.filter(Depreciation.status == status)

    return query.order_by(Depreciation.depreciation_date.desc()).all()


@router.post("/depreciations/{depreciation_id}/post")
def post_depreciation(
    depreciation_id: int,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """Post depreciation to GL."""
    depreciation = db.query(Depreciation).filter(Depreciation.id == depreciation_id).first()
    if not depreciation:
        raise HTTPException(status_code=404, detail="Depreciation not found")

    depreciation.status = "posted"
    depreciation.posted_by_id = user_id
    depreciation.posted_date = datetime.utcnow()
    db.commit()

    create_audit_log(db, user_id, "post", "Depreciation", depreciation.id,
                    f"Posted depreciation {depreciation.depreciation_number}", tenant_id)
    db.commit()

    return {"message": "Depreciation posted", "depreciation_number": depreciation.depreciation_number}


# ============================================================================
# Process 55: GST/VAT Filing
# ============================================================================

@router.post("/tax-filings", response_model=TaxFilingResponse)
def create_tax_filing(
    filing: TaxFilingCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """
    Process 55: GST/VAT Filing
    Input: Transaction data → Compute returns
    Output: Tax report
    """
    # Generate filing number
    count = db.query(TaxFiling).count()
    filing_number = f"TAX-{datetime.now().year}-{count + 1:05d}"

    db_filing = TaxFiling(
        filing_number=filing_number,
        tax_type=filing.tax_type,
        period_start=filing.period_start,
        period_end=filing.period_end,
        due_date=filing.due_date,
        notes=filing.notes,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_filing)
    db.commit()
    db.refresh(db_filing)

    create_audit_log(db, user_id, "create", "TaxFiling", db_filing.id,
                    f"Created tax filing {filing_number}", tenant_id)
    db.commit()

    return db_filing


@router.get("/tax-filings", response_model=List[TaxFilingResponse])
def list_tax_filings(
    tax_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List tax filings."""
    query = db.query(TaxFiling)
    query = apply_tenant_filter(query, TaxFiling, tenant_id)

    if tax_type:
        query = query.filter(TaxFiling.tax_type == tax_type)
    if status:
        query = query.filter(TaxFiling.status == status)

    return query.order_by(TaxFiling.due_date.desc()).all()


@router.post("/tax-filings/{filing_id}/calculate")
def calculate_tax_filing(
    filing_id: int,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """Calculate tax for a filing period."""
    filing = db.query(TaxFiling).filter(TaxFiling.id == filing_id).first()
    if not filing:
        raise HTTPException(status_code=404, detail="Tax filing not found")

    # Get invoices in period for output tax
    invoices_query = db.query(Invoice).filter(
        Invoice.invoice_date >= filing.period_start,
        Invoice.invoice_date <= filing.period_end
    )
    invoices_query = apply_tenant_filter(invoices_query, Invoice, tenant_id)
    invoices = invoices_query.all()

    output_tax = sum(inv.tax_amount for inv in invoices)
    total_sales = sum(inv.subtotal for inv in invoices)

    # Get expenses in period for input tax
    expenses_query = db.query(Expense).filter(
        Expense.expense_date >= filing.period_start,
        Expense.expense_date <= filing.period_end
    )
    expenses_query = apply_tenant_filter(expenses_query, Expense, tenant_id)
    expenses = expenses_query.all()

    input_tax = sum(exp.tax_amount for exp in expenses)
    total_purchases = sum(exp.amount for exp in expenses)

    # Calculate net tax
    net_tax = output_tax - input_tax

    # Update filing
    filing.output_tax = output_tax
    filing.input_tax = input_tax
    filing.net_tax = net_tax
    filing.total_sales = total_sales
    filing.total_purchases = total_purchases
    filing.status = "calculated"

    db.commit()

    create_audit_log(db, user_id, "update", "TaxFiling", filing.id,
                    f"Calculated tax for filing {filing.filing_number}", tenant_id)
    db.commit()

    return {
        "message": "Tax calculated",
        "filing_number": filing.filing_number,
        "output_tax": output_tax,
        "input_tax": input_tax,
        "net_tax": net_tax,
    }


@router.post("/tax-filings/{filing_id}/file")
def file_tax_return(
    filing_id: int,
    confirmation_number: str,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """File tax return."""
    filing = db.query(TaxFiling).filter(TaxFiling.id == filing_id).first()
    if not filing:
        raise HTTPException(status_code=404, detail="Tax filing not found")

    filing.status = "filed"
    filing.filed_by_id = user_id
    filing.filing_date = datetime.utcnow().date()
    filing.confirmation_number = confirmation_number
    db.commit()

    create_audit_log(db, user_id, "update", "TaxFiling", filing.id,
                    f"Filed tax return {filing.filing_number}", tenant_id)
    db.commit()

    return {"message": "Tax return filed", "filing_number": filing.filing_number}


# ============================================================================
# Process 56: Budget Allocation
# ============================================================================

@router.post("/budgets", response_model=BudgetResponse)
def create_budget(
    budget: BudgetCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """
    Process 56: Budget Allocation
    Input: Dept request → Approve
    Output: Budget file
    """
    # Generate budget number
    count = db.query(Budget).count()
    budget_number = f"BUD-{datetime.now().year}-{count + 1:05d}"

    db_budget = Budget(
        budget_number=budget_number,
        budget_name=budget.budget_name,
        description=budget.description,
        fiscal_year=budget.fiscal_year,
        period_start=budget.period_start,
        period_end=budget.period_end,
        department=budget.department,
        cost_center_id=budget.cost_center_id,
        total_budget_amount=budget.total_budget_amount,
        remaining_amount=budget.total_budget_amount,
        submitted_by_id=user_id,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_budget)
    db.flush()

    # Add budget lines if provided
    if budget.lines:
        for line in budget.lines:
            db_line = BudgetLine(
                budget_id=db_budget.id,
                account_id=line.account_id,
                budgeted_amount=line.budgeted_amount,
                remaining_amount=line.budgeted_amount,
                description=line.description,
                tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
            )
            db.add(db_line)

    db.commit()
    db.refresh(db_budget)

    create_audit_log(db, user_id, "create", "Budget", db_budget.id,
                    f"Created budget {budget_number}", tenant_id)
    db.commit()

    return db_budget


@router.get("/budgets", response_model=List[BudgetResponse])
def list_budgets(
    fiscal_year: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List budgets."""
    query = db.query(Budget)
    query = apply_tenant_filter(query, Budget, tenant_id)

    if fiscal_year:
        query = query.filter(Budget.fiscal_year == fiscal_year)
    if status:
        query = query.filter(Budget.status == status)

    return query.order_by(Budget.fiscal_year.desc(), Budget.created_at.desc()).all()


@router.post("/budgets/{budget_id}/approve")
def approve_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """Approve a budget."""
    budget = db.query(Budget).filter(Budget.id == budget_id).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")

    budget.status = "approved"
    budget.approved_by_id = user_id
    budget.approval_date = datetime.utcnow()
    db.commit()

    create_audit_log(db, user_id, "approve", "Budget", budget.id,
                    f"Approved budget {budget.budget_number}", tenant_id)
    db.commit()

    return {"message": "Budget approved", "budget_number": budget.budget_number}


# ============================================================================
# Process 57: Cost Center Accounting
# ============================================================================

@router.post("/cost-centers", response_model=CostCenterResponse)
def create_cost_center(
    cost_center: CostCenterCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """
    Process 57: Cost Center Accounting
    Input: Expense posting → Assign cost centers
    Output: Cost report
    """
    # Check for duplicate code
    existing = db.query(CostCenter).filter(
        CostCenter.cost_center_code == cost_center.cost_center_code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Cost center code already exists")

    db_cost_center = CostCenter(
        cost_center_code=cost_center.cost_center_code,
        cost_center_name=cost_center.cost_center_name,
        description=cost_center.description,
        department=cost_center.department,
        parent_cost_center_id=cost_center.parent_cost_center_id,
        manager_name=cost_center.manager_name,
        manager_id=cost_center.manager_id,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_cost_center)
    db.commit()
    db.refresh(db_cost_center)

    create_audit_log(db, user_id, "create", "CostCenter", db_cost_center.id,
                    f"Created cost center {cost_center.cost_center_code}", tenant_id)
    db.commit()

    return db_cost_center


@router.get("/cost-centers", response_model=List[CostCenterResponse])
def list_cost_centers(
    is_active: Optional[bool] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List cost centers."""
    query = db.query(CostCenter)
    query = apply_tenant_filter(query, CostCenter, tenant_id)

    if is_active is not None:
        query = query.filter(CostCenter.is_active == is_active)
    if department:
        query = query.filter(CostCenter.department == department)

    return query.order_by(CostCenter.cost_center_code).all()


@router.get("/cost-centers/{cost_center_id}/report")
def get_cost_center_report(
    cost_center_id: int,
    period_start: str,
    period_end: str,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """Get cost center expense report."""
    from datetime import datetime as dt

    period_start_date = dt.strptime(period_start, "%Y-%m-%d").date()
    period_end_date = dt.strptime(period_end, "%Y-%m-%d").date()

    # Get expenses for this cost center
    expenses_query = db.query(Expense).filter(
        Expense.cost_center_id == cost_center_id,
        Expense.expense_date >= period_start_date,
        Expense.expense_date <= period_end_date
    )
    expenses_query = apply_tenant_filter(expenses_query, Expense, tenant_id)
    expenses = expenses_query.all()

    total_expenses = sum(exp.total_amount for exp in expenses)
    expense_count = len(expenses)

    # Get budget for this cost center
    budget = db.query(Budget).filter(
        Budget.cost_center_id == cost_center_id,
        Budget.status == "approved"
    ).first()

    return {
        "cost_center_id": cost_center_id,
        "period_start": period_start_date,
        "period_end": period_end_date,
        "total_expenses": total_expenses,
        "expense_count": expense_count,
        "budgeted_amount": budget.total_budget_amount if budget else 0,
        "variance": (budget.total_budget_amount - total_expenses) if budget else None,
    }


# ============================================================================
# Process 58: Financial Closing
# ============================================================================

@router.post("/financial-periods", response_model=FinancialPeriodResponse)
def create_financial_period(
    period: FinancialPeriodCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """
    Process 58: Financial Closing
    Input: Ledger data → Trial balance
    Output: Financial statements
    """
    # Generate period number
    count = db.query(FinancialPeriod).count()
    period_number = f"FP-{datetime.now().year}-{count + 1:04d}"

    db_period = FinancialPeriod(
        period_number=period_number,
        period_name=period.period_name,
        fiscal_year=period.fiscal_year,
        period_start=period.period_start,
        period_end=period.period_end,
        is_year_end=period.is_year_end,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_period)
    db.commit()
    db.refresh(db_period)

    create_audit_log(db, user_id, "create", "FinancialPeriod", db_period.id,
                    f"Created financial period {period_number}", tenant_id)
    db.commit()

    return db_period


@router.get("/financial-periods", response_model=List[FinancialPeriodResponse])
def list_financial_periods(
    fiscal_year: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List financial periods."""
    query = db.query(FinancialPeriod)
    query = apply_tenant_filter(query, FinancialPeriod, tenant_id)

    if fiscal_year:
        query = query.filter(FinancialPeriod.fiscal_year == fiscal_year)
    if status:
        query = query.filter(FinancialPeriod.status == status)

    return query.order_by(FinancialPeriod.period_start.desc()).all()


@router.post("/financial-periods/{period_id}/close")
def close_financial_period(
    period_id: int,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """Close a financial period (trial balance and lock)."""
    period = db.query(FinancialPeriod).filter(FinancialPeriod.id == period_id).first()
    if not period:
        raise HTTPException(status_code=404, detail="Financial period not found")

    # Calculate trial balance from all accounts
    accounts_query = db.query(ChartOfAccounts)
    accounts_query = apply_tenant_filter(accounts_query, ChartOfAccounts, tenant_id)
    accounts = accounts_query.all()

    total_debits = 0
    total_credits = 0

    for account in accounts:
        if account.account_type in ["asset", "expense"]:
            # Debit balance accounts
            if account.current_balance >= 0:
                total_debits += account.current_balance
            else:
                total_credits += abs(account.current_balance)
        else:  # liability, equity, revenue
            # Credit balance accounts
            if account.current_balance >= 0:
                total_credits += account.current_balance
            else:
                total_debits += abs(account.current_balance)

    period.total_debits = total_debits
    period.total_credits = total_credits
    period.is_balanced = (total_debits == total_credits)
    period.status = "closed"
    period.closed_by_id = user_id
    period.closed_date = datetime.utcnow()

    db.commit()

    create_audit_log(db, user_id, "update", "FinancialPeriod", period.id,
                    f"Closed financial period {period.period_number}", tenant_id)
    db.commit()

    return {
        "message": "Financial period closed",
        "period_number": period.period_number,
        "is_balanced": period.is_balanced,
        "total_debits": total_debits,
        "total_credits": total_credits,
    }


# ============================================================================
# Process 59: Cash Flow Reporting
# ============================================================================

@router.post("/cash-flows", response_model=CashFlowResponse)
def create_cash_flow_report(
    cash_flow: CashFlowCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
):
    """
    Process 59: Cash Flow Reporting
    Input: Receipts & payments → Prepare statement
    Output: Cash flow
    """
    # Generate report number
    count = db.query(CashFlow).count()
    report_number = f"CF-{datetime.now().year}-{count + 1:05d}"

    # Get cash accounts
    cash_accounts_query = db.query(ChartOfAccounts).filter(
        ChartOfAccounts.account_type == "asset",
        ChartOfAccounts.account_subtype == "Cash"
    )
    cash_accounts_query = apply_tenant_filter(cash_accounts_query, ChartOfAccounts, tenant_id)
    cash_accounts = cash_accounts_query.all()

    opening_cash = sum(acc.opening_balance for acc in cash_accounts)
    closing_cash = sum(acc.current_balance for acc in cash_accounts)
    net_change = closing_cash - opening_cash

    # Get receipts and payments in period
    receipts_query = db.query(CustomerReceipt).filter(
        CustomerReceipt.receipt_date >= cash_flow.period_start,
        CustomerReceipt.receipt_date <= cash_flow.period_end
    )
    receipts_query = apply_tenant_filter(receipts_query, CustomerReceipt, tenant_id)
    receipts = receipts_query.all()

    payments_query = db.query(VendorPayment).filter(
        VendorPayment.payment_date >= cash_flow.period_start,
        VendorPayment.payment_date <= cash_flow.period_end
    )
    payments_query = apply_tenant_filter(payments_query, VendorPayment, tenant_id)
    payments = payments_query.all()

    operating_inflows = sum(r.receipt_amount for r in receipts)
    operating_outflows = sum(p.payment_amount for p in payments)
    net_operating = operating_inflows - operating_outflows

    db_cash_flow = CashFlow(
        report_number=report_number,
        period_start=cash_flow.period_start,
        period_end=cash_flow.period_end,
        report_date=cash_flow.report_date,
        opening_cash=opening_cash,
        closing_cash=closing_cash,
        net_change=net_change,
        operating_inflows=operating_inflows,
        operating_outflows=operating_outflows,
        net_operating=net_operating,
        notes=cash_flow.notes,
        tenant_id=tenant_id if settings.ENABLE_TENANCY else None,
    )
    db.add(db_cash_flow)
    db.commit()
    db.refresh(db_cash_flow)

    create_audit_log(db, user_id, "create", "CashFlow", db_cash_flow.id,
                    f"Created cash flow report {report_number}", tenant_id)
    db.commit()

    return db_cash_flow


@router.get("/cash-flows", response_model=List[CashFlowResponse])
def list_cash_flow_reports(
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """List cash flow reports."""
    query = db.query(CashFlow)
    query = apply_tenant_filter(query, CashFlow, tenant_id)
    return query.order_by(CashFlow.report_date.desc()).all()


# ============================================================================
# Process 60: Audit Log Review
# ============================================================================

@router.get("/audit-logs", response_model=List[AuditLogResponse])
def list_audit_logs(
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    user_id: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """
    Process 60: Audit Log Review
    Input: System logs → Verify & certify
    Output: Audit report
    """
    query = db.query(AuditLog)
    query = apply_tenant_filter(query, AuditLog, tenant_id)

    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if action:
        query = query.filter(AuditLog.action == action)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()


@router.get("/audit-logs/summary")
def get_audit_log_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """Get audit log summary statistics."""
    from datetime import datetime as dt
    from sqlalchemy import func

    query = db.query(AuditLog)
    query = apply_tenant_filter(query, AuditLog, tenant_id)

    if start_date:
        start_dt = dt.strptime(start_date, "%Y-%m-%d")
        query = query.filter(AuditLog.timestamp >= start_dt)
    if end_date:
        end_dt = dt.strptime(end_date, "%Y-%m-%d")
        query = query.filter(AuditLog.timestamp <= end_dt)

    total_logs = query.count()

    # Count by action
    action_counts = db.query(
        AuditLog.action,
        func.count(AuditLog.id).label('count')
    ).group_by(AuditLog.action).all()

    # Count by entity type
    entity_counts = db.query(
        AuditLog.entity_type,
        func.count(AuditLog.id).label('count')
    ).group_by(AuditLog.entity_type).all()

    return {
        "total_logs": total_logs,
        "actions": {action: count for action, count in action_counts},
        "entities": {entity: count for entity, count in entity_counts},
        "start_date": start_date,
        "end_date": end_date,
    }


# ============================================================================
# Dashboard & Analytics
# ============================================================================

@router.get("/finance/dashboard")
def get_finance_dashboard(
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None,
):
    """Get finance dashboard summary."""
    # Invoices
    invoices_query = db.query(Invoice)
    invoices_query = apply_tenant_filter(invoices_query, Invoice, tenant_id)

    total_invoices = invoices_query.count()
    outstanding_invoices = invoices_query.filter(Invoice.status.in_(["sent", "partially_paid", "overdue"])).count()
    overdue_invoices = invoices_query.filter(Invoice.status == "overdue").count()

    # Expenses
    expenses_query = db.query(Expense)
    expenses_query = apply_tenant_filter(expenses_query, Expense, tenant_id)

    total_expenses = expenses_query.count()
    pending_expenses = expenses_query.filter(Expense.status == "submitted").count()

    # Assets
    assets_query = db.query(FixedAsset)
    assets_query = apply_tenant_filter(assets_query, FixedAsset, tenant_id)

    total_assets = assets_query.count()
    active_assets = assets_query.filter(FixedAsset.status == "active").count()

    # Tax filings
    tax_filings_query = db.query(TaxFiling)
    tax_filings_query = apply_tenant_filter(tax_filings_query, TaxFiling, tenant_id)

    pending_tax_filings = tax_filings_query.filter(TaxFiling.status.in_(["draft", "calculated"])).count()

    # Budgets
    budgets_query = db.query(Budget)
    budgets_query = apply_tenant_filter(budgets_query, Budget, tenant_id)

    active_budgets = budgets_query.filter(Budget.status == "approved").count()

    return {
        "invoices": {
            "total": total_invoices,
            "outstanding": outstanding_invoices,
            "overdue": overdue_invoices,
        },
        "expenses": {
            "total": total_expenses,
            "pending_approval": pending_expenses,
        },
        "assets": {
            "total": total_assets,
            "active": active_assets,
        },
        "tax_filings": {
            "pending": pending_tax_filings,
        },
        "budgets": {
            "active": active_budgets,
        },
    }
