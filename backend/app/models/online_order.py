"""
Online Order model - e-commerce order processing.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class OnlineOrderStatus(str, enum.Enum):
    CART = "cart"
    PENDING_PAYMENT = "pending_payment"
    PAYMENT_FAILED = "payment_failed"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    UPI = "upi"
    NET_BANKING = "net_banking"
    WALLET = "wallet"
    COD = "cod"
    EMI = "emi"


class OnlineOrder(Base):
    __tablename__ = "online_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True, nullable=False)

    # Customer
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    customer_email = Column(String, nullable=False)
    customer_phone = Column(String, nullable=True)

    # Order details
    status = Column(Enum(OnlineOrderStatus), default=OnlineOrderStatus.CART)
    order_date = Column(DateTime, nullable=True)

    # Items (stored as JSON)
    items = Column(Text, nullable=False)  # JSON array of {sku, quantity, price, title}

    # Amounts (in cents)
    subtotal = Column(Integer, default=0)
    shipping_charges = Column(Integer, default=0)
    tax_amount = Column(Integer, default=0)
    discount_amount = Column(Integer, default=0)
    total_amount = Column(Integer, default=0)

    # Discounts
    coupon_code = Column(String, nullable=True)
    loyalty_points_used = Column(Integer, default=0)

    # Payment
    payment_method = Column(Enum(PaymentMethod), nullable=True)
    payment_status = Column(String, default="pending")  # pending, completed, failed, refunded
    payment_transaction_id = Column(String, nullable=True)
    payment_gateway = Column(String, nullable=True)  # razorpay, stripe, paypal
    paid_at = Column(DateTime, nullable=True)

    # Shipping address
    shipping_name = Column(String, nullable=True)
    shipping_address_line1 = Column(String, nullable=True)
    shipping_address_line2 = Column(String, nullable=True)
    shipping_city = Column(String, nullable=True)
    shipping_state = Column(String, nullable=True)
    shipping_postal_code = Column(String, nullable=True)
    shipping_country = Column(String, nullable=True)

    # Billing address
    billing_name = Column(String, nullable=True)
    billing_address_line1 = Column(String, nullable=True)
    billing_address_line2 = Column(String, nullable=True)
    billing_city = Column(String, nullable=True)
    billing_state = Column(String, nullable=True)
    billing_postal_code = Column(String, nullable=True)
    billing_country = Column(String, nullable=True)

    # Fulfillment
    shipment_id = Column(Integer, ForeignKey("shipments.id"), nullable=True)
    tracking_number = Column(String, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    # Notes
    customer_notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)

    # Source
    source_channel = Column(String, default="website")  # website, mobile_app, marketplace

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    customer = relationship("Customer")

    def __repr__(self):
        return f"<OnlineOrder {self.order_number}>"
