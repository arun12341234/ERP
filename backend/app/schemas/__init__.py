"""Pydantic schemas for request/response validation."""
from app.schemas.user import User, UserCreate, UserUpdate, Token
from app.schemas.item import Item, ItemCreate, ItemUpdate
from app.schemas.lead import Lead, LeadCreate, LeadUpdate
from app.schemas.customer import Customer, CustomerCreate, CustomerUpdate
from app.schemas.opportunity import Opportunity, OpportunityCreate, OpportunityUpdate
from app.schemas.quote import Quote, QuoteCreate, QuoteUpdate
from app.schemas.sales_order import SalesOrder, SalesOrderCreate, SalesOrderUpdate
from app.schemas.feedback import Feedback, FeedbackCreate, FeedbackUpdate
from app.schemas.support_ticket import SupportTicket, SupportTicketCreate, SupportTicketUpdate
from app.schemas.contract import Contract, ContractCreate, ContractUpdate

__all__ = [
    "User", "UserCreate", "UserUpdate", "Token",
    "Item", "ItemCreate", "ItemUpdate",
    "Lead", "LeadCreate", "LeadUpdate",
    "Customer", "CustomerCreate", "CustomerUpdate",
    "Opportunity", "OpportunityCreate", "OpportunityUpdate",
    "Quote", "QuoteCreate", "QuoteUpdate",
    "SalesOrder", "SalesOrderCreate", "SalesOrderUpdate",
    "Feedback", "FeedbackCreate", "FeedbackUpdate",
    "SupportTicket", "SupportTicketCreate", "SupportTicketUpdate",
    "Contract", "ContractCreate", "ContractUpdate",
]
