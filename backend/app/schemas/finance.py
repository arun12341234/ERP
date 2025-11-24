"""
Finance & Accounting schemas for request/response validation.
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel


# Chart of Accounts schemas
class ChartOfAccountsCreate(BaseModel):
    account_code: str
    account_name: str
    account_type: str
    account_subtype: Optional[str] = None
    parent_account_id: Optional[int] = None
    level: int = 1
    is_control_account: bool = False
    allow_posting: bool = True
    opening_balance: int = 0
    description: Optional[str] = None


class ChartOfAccountsResponse(BaseModel):
    id: int
    account_code: str
    account_name: str
    account_type: str
    account_subtype: Optional[str]
    parent_account_id: Optional[int]
    level: int
    is_active: bool
    is_control_account: bool
    allow_posting: bool
    opening_balance: int
    current_balance: int
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Invoice schemas
class InvoiceCreate(BaseModel):
    customer_id: int
    sales_order_id: Optional[int] = None
    invoice_date: date
    due_date: date
    payment_terms: Optional[str] = None
    subtotal: int
    tax_amount: int = 0
    discount_amount: int = 0
    total_amount: int
    notes: Optional[str] = None
    terms_conditions: Optional[str] = None


class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    customer_id: int
    sales_order_id: Optional[int]
    invoice_date: date
    due_date: date
    payment_terms: Optional[str]
    subtotal: int
    tax_amount: int
    discount_amount: int
    total_amount: int
    amount_paid: int
    amount_due: int
    status: str
    notes: Optional[str]
    terms_conditions: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Expense schemas
class ExpenseCreate(BaseModel):
    expense_date: date
    category: str
    description: str
    amount: int
    tax_amount: int = 0
    total_amount: int
    vendor_id: Optional[int] = None
    payee_name: Optional[str] = None
    account_id: Optional[int] = None
    cost_center_id: Optional[int] = None
    notes: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: int
    expense_number: str
    expense_date: date
    category: str
    description: str
    amount: int
    tax_amount: int
    total_amount: int
    vendor_id: Optional[int]
    payee_name: Optional[str]
    account_id: Optional[int]
    cost_center_id: Optional[int]
    status: str
    submitted_by_id: Optional[int]
    approved_by_id: Optional[int]
    approval_date: Optional[datetime]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Vendor Payment schemas
class VendorPaymentCreate(BaseModel):
    vendor_id: int
    payment_date: date
    payment_method: str
    payment_amount: int
    reference_number: Optional[str] = None
    bank_account_id: Optional[int] = None
    notes: Optional[str] = None


class VendorPaymentResponse(BaseModel):
    id: int
    payment_number: str
    vendor_id: int
    payment_date: date
    payment_method: str
    reference_number: Optional[str]
    payment_amount: int
    bank_account_id: Optional[int]
    status: str
    approved_by_id: Optional[int]
    approval_date: Optional[datetime]
    processed_by_id: Optional[int]
    processed_date: Optional[datetime]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Customer Receipt schemas
class CustomerReceiptCreate(BaseModel):
    customer_id: int
    invoice_id: Optional[int] = None
    receipt_date: date
    receipt_method: str
    receipt_amount: int
    reference_number: Optional[str] = None
    bank_account_id: Optional[int] = None
    notes: Optional[str] = None


class CustomerReceiptResponse(BaseModel):
    id: int
    receipt_number: str
    customer_id: int
    invoice_id: Optional[int]
    receipt_date: date
    receipt_method: str
    reference_number: Optional[str]
    receipt_amount: int
    bank_account_id: Optional[int]
    status: str
    recorded_by_id: Optional[int]
    recorded_date: Optional[datetime]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Journal Entry schemas
class JournalEntryLineCreate(BaseModel):
    account_id: int
    debit_amount: int = 0
    credit_amount: int = 0
    description: Optional[str] = None
    cost_center_id: Optional[int] = None


class JournalEntryCreate(BaseModel):
    entry_date: date
    entry_type: str = "standard"
    description: str
    reference: Optional[str] = None
    lines: List[JournalEntryLineCreate]


class JournalEntryLineResponse(BaseModel):
    id: int
    account_id: int
    debit_amount: int
    credit_amount: int
    description: Optional[str]
    cost_center_id: Optional[int]

    class Config:
        from_attributes = True


class JournalEntryResponse(BaseModel):
    id: int
    entry_number: str
    entry_date: date
    entry_type: str
    description: str
    status: str
    posted_by_id: Optional[int]
    posted_date: Optional[datetime]
    is_reversed: bool
    reversed_by_id: Optional[int]
    reversed_date: Optional[datetime]
    reference: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Bank Reconciliation schemas
class BankReconciliationLineCreate(BaseModel):
    transaction_date: date
    description: str
    reference: Optional[str] = None
    amount: int
    is_matched: bool = False
    matched_transaction_id: Optional[int] = None


class BankReconciliationCreate(BaseModel):
    bank_account_id: int
    statement_date: date
    reconciliation_date: date
    opening_balance: int = 0
    closing_balance: int = 0
    statement_balance: int
    book_balance: int
    notes: Optional[str] = None
    lines: Optional[List[BankReconciliationLineCreate]] = None


class BankReconciliationResponse(BaseModel):
    id: int
    reconciliation_number: str
    bank_account_id: int
    statement_date: date
    reconciliation_date: date
    opening_balance: int
    closing_balance: int
    statement_balance: int
    book_balance: int
    difference: int
    status: str
    reconciled_by_id: Optional[int]
    approved_by_id: Optional[int]
    approved_date: Optional[datetime]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Fixed Asset schemas
class FixedAssetCreate(BaseModel):
    asset_name: str
    description: Optional[str] = None
    category: str
    acquisition_date: date
    acquisition_cost: int
    vendor_id: Optional[int] = None
    location: Optional[str] = None
    department: Optional[str] = None
    custodian: Optional[str] = None
    depreciation_method: str = "straight_line"
    useful_life_years: int
    salvage_value: int = 0
    asset_account_id: Optional[int] = None
    depreciation_account_id: Optional[int] = None
    accumulated_depreciation_account_id: Optional[int] = None


class FixedAssetResponse(BaseModel):
    id: int
    asset_number: str
    asset_name: str
    description: Optional[str]
    category: str
    acquisition_date: date
    acquisition_cost: int
    vendor_id: Optional[int]
    location: Optional[str]
    department: Optional[str]
    custodian: Optional[str]
    depreciation_method: str
    useful_life_years: int
    salvage_value: int
    accumulated_depreciation: int
    net_book_value: int
    asset_account_id: Optional[int]
    depreciation_account_id: Optional[int]
    accumulated_depreciation_account_id: Optional[int]
    status: str
    disposal_date: Optional[date]
    disposal_proceeds: int
    created_at: datetime

    class Config:
        from_attributes = True


# Depreciation schemas
class DepreciationCreate(BaseModel):
    asset_id: int
    period_start: date
    period_end: date
    depreciation_date: date
    depreciation_amount: int
    accumulated_depreciation: int
    net_book_value: int


class DepreciationResponse(BaseModel):
    id: int
    depreciation_number: str
    asset_id: int
    period_start: date
    period_end: date
    depreciation_date: date
    depreciation_amount: int
    accumulated_depreciation: int
    net_book_value: int
    status: str
    journal_entry_id: Optional[int]
    posted_by_id: Optional[int]
    posted_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Tax Filing schemas
class TaxFilingCreate(BaseModel):
    tax_type: str
    period_start: date
    period_end: date
    due_date: date
    notes: Optional[str] = None


class TaxFilingResponse(BaseModel):
    id: int
    filing_number: str
    tax_type: str
    period_start: date
    period_end: date
    filing_date: Optional[date]
    due_date: date
    output_tax: int
    input_tax: int
    net_tax: int
    total_sales: int
    total_purchases: int
    status: str
    filed_by_id: Optional[int]
    confirmation_number: Optional[str]
    payment_date: Optional[date]
    payment_reference: Optional[str]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Budget schemas
class BudgetLineCreate(BaseModel):
    account_id: int
    budgeted_amount: int
    description: Optional[str] = None


class BudgetCreate(BaseModel):
    budget_name: str
    description: Optional[str] = None
    fiscal_year: int
    period_start: date
    period_end: date
    department: Optional[str] = None
    cost_center_id: Optional[int] = None
    total_budget_amount: int
    lines: Optional[List[BudgetLineCreate]] = None


class BudgetResponse(BaseModel):
    id: int
    budget_number: str
    budget_name: str
    description: Optional[str]
    fiscal_year: int
    period_start: date
    period_end: date
    department: Optional[str]
    cost_center_id: Optional[int]
    total_budget_amount: int
    allocated_amount: int
    spent_amount: int
    remaining_amount: int
    status: str
    submitted_by_id: Optional[int]
    approved_by_id: Optional[int]
    approval_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Cost Center schemas
class CostCenterCreate(BaseModel):
    cost_center_code: str
    cost_center_name: str
    description: Optional[str] = None
    department: Optional[str] = None
    parent_cost_center_id: Optional[int] = None
    manager_name: Optional[str] = None
    manager_id: Optional[int] = None


class CostCenterResponse(BaseModel):
    id: int
    cost_center_code: str
    cost_center_name: str
    description: Optional[str]
    department: Optional[str]
    parent_cost_center_id: Optional[int]
    manager_name: Optional[str]
    manager_id: Optional[int]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Financial Period schemas
class FinancialPeriodCreate(BaseModel):
    period_name: str
    fiscal_year: int
    period_start: date
    period_end: date
    is_year_end: bool = False


class FinancialPeriodResponse(BaseModel):
    id: int
    period_number: str
    period_name: str
    fiscal_year: int
    period_start: date
    period_end: date
    status: str
    is_year_end: bool
    closed_by_id: Optional[int]
    closed_date: Optional[datetime]
    total_debits: int
    total_credits: int
    is_balanced: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Cash Flow schemas
class CashFlowCreate(BaseModel):
    period_start: date
    period_end: date
    report_date: date
    notes: Optional[str] = None


class CashFlowResponse(BaseModel):
    id: int
    report_number: str
    period_start: date
    period_end: date
    report_date: date
    opening_cash: int
    closing_cash: int
    net_change: int
    operating_inflows: int
    operating_outflows: int
    net_operating: int
    investing_inflows: int
    investing_outflows: int
    net_investing: int
    financing_inflows: int
    financing_outflows: int
    net_financing: int
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Audit Log schemas
class AuditLogCreate(BaseModel):
    action: str
    severity: str = "info"
    entity_type: str
    entity_id: Optional[int] = None
    entity_identifier: Optional[str] = None
    description: str
    changes: Optional[str] = None
    user_ip: Optional[str] = None
    request_method: Optional[str] = None
    request_path: Optional[str] = None


class AuditLogResponse(BaseModel):
    id: int
    timestamp: datetime
    user_id: Optional[int]
    username: Optional[str]
    user_ip: Optional[str]
    action: str
    severity: str
    entity_type: str
    entity_id: Optional[int]
    entity_identifier: Optional[str]
    description: str
    changes: Optional[str]
    request_method: Optional[str]
    request_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
