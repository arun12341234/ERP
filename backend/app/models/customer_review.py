"""
Customer Review model - product reviews and ratings management.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class ReviewStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"


class ReviewSource(str, enum.Enum):
    WEBSITE = "website"
    MOBILE_APP = "mobile_app"
    EMAIL_REQUEST = "email_request"
    MARKETPLACE = "marketplace"


class CustomerReview(Base):
    __tablename__ = "customer_reviews"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(String, unique=True, index=True, nullable=False)

    # Product
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    website_product_id = Column(Integer, ForeignKey("website_products.id"), nullable=True)

    # Customer
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=True)

    # Order (verified purchase)
    online_order_id = Column(Integer, ForeignKey("online_orders.id"), nullable=True)
    is_verified_purchase = Column(Integer, default=0)  # boolean as int

    # Rating
    overall_rating = Column(Integer, nullable=False)  # 1-5 stars
    quality_rating = Column(Integer, nullable=True)  # 1-5 stars
    value_rating = Column(Integer, nullable=True)  # 1-5 stars
    delivery_rating = Column(Integer, nullable=True)  # 1-5 stars

    # Review content
    review_title = Column(String, nullable=True)
    review_text = Column(Text, nullable=False)

    # Pros and Cons
    pros = Column(Text, nullable=True)  # JSON array
    cons = Column(Text, nullable=True)  # JSON array

    # Media
    images = Column(Text, nullable=True)  # JSON array of URLs
    videos = Column(Text, nullable=True)  # JSON array of URLs

    # Recommendation
    would_recommend = Column(Integer, nullable=True)  # boolean as int

    # Status
    status = Column(Enum(ReviewStatus), default=ReviewStatus.PENDING)

    # Moderation
    moderated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    moderation_date = Column(DateTime, nullable=True)
    moderation_notes = Column(Text, nullable=True)

    # Flags
    is_featured = Column(Integer, default=0)  # boolean as int
    is_flagged = Column(Integer, default=0)  # boolean as int
    flag_count = Column(Integer, default=0)

    # Helpfulness
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)

    # Seller response
    seller_response = Column(Text, nullable=True)
    seller_response_date = Column(DateTime, nullable=True)
    seller_response_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Source
    review_source = Column(Enum(ReviewSource), default=ReviewSource.WEBSITE)

    # Incentives (rewards for leaving review)
    loyalty_points_awarded = Column(Integer, default=0)
    incentive_given = Column(String, nullable=True)

    # Timestamps
    review_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    customer = relationship("Customer")
    product = relationship("Product")

    def __repr__(self):
        return f"<CustomerReview {self.review_id} - {self.overall_rating} stars>"


class ReviewHelpfulness(Base):
    __tablename__ = "review_helpfulness"

    id = Column(Integer, primary_key=True, index=True)

    # Review
    review_id = Column(Integer, ForeignKey("customer_reviews.id"), nullable=False)

    # User (can be customer or anonymous)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    session_id = Column(String, nullable=True)  # for anonymous votes

    # Vote
    is_helpful = Column(Integer, nullable=False)  # 1 = helpful, 0 = not helpful

    # Timestamps
    voted_at = Column(DateTime, default=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<ReviewHelpfulness review_id={self.review_id}>"
