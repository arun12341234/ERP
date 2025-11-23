"""Database models."""
from app.models.user import User
from app.models.item import Item
from app.models.lead import Lead
from app.models.customer import Customer
from app.models.opportunity import Opportunity
from app.models.quote import Quote
from app.models.sales_order import SalesOrder
from app.models.feedback import Feedback
from app.models.support_ticket import SupportTicket
from app.models.contract import Contract

__all__ = [
    "User",
    "Item",
    "Lead",
    "Customer",
    "Opportunity",
    "Quote",
    "SalesOrder",
    "Feedback",
    "SupportTicket",
    "Contract",
]
