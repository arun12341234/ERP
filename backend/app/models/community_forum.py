"""
Community Forum model - customer community and discussion forums.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class ForumCategory(str, enum.Enum):
    GENERAL_DISCUSSION = "general_discussion"
    PRODUCT_REVIEWS = "product_reviews"
    HELP_SUPPORT = "help_support"
    FEATURE_REQUESTS = "feature_requests"
    BUG_REPORTS = "bug_reports"
    ANNOUNCEMENTS = "announcements"
    OFF_TOPIC = "off_topic"


class PostStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"
    ARCHIVED = "archived"


class PostType(str, enum.Enum):
    QUESTION = "question"
    DISCUSSION = "discussion"
    ANNOUNCEMENT = "announcement"
    POLL = "poll"


class ForumThread(Base):
    __tablename__ = "forum_threads"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, unique=True, index=True, nullable=False)

    # Author
    author_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    author_name = Column(String, nullable=False)

    # Thread details
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)

    # Classification
    category = Column(Enum(ForumCategory), nullable=False)
    post_type = Column(Enum(PostType), default=PostType.DISCUSSION)
    tags = Column(Text, nullable=True)  # JSON array

    # Status
    status = Column(Enum(PostStatus), default=PostStatus.PENDING_APPROVAL)

    # Moderation
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approval_date = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Flags
    is_pinned = Column(Integer, default=0)  # boolean as int
    is_locked = Column(Integer, default=0)  # boolean as int
    is_featured = Column(Integer, default=0)  # boolean as int

    # Engagement
    view_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)

    # Question-specific (for Q&A type posts)
    has_accepted_answer = Column(Integer, default=0)  # boolean as int
    accepted_answer_id = Column(Integer, nullable=True)

    # Last activity
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    last_reply_by_id = Column(Integer, ForeignKey("customers.id"), nullable=True)

    # Attachments
    attachments = Column(Text, nullable=True)  # JSON array

    # SEO
    meta_description = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    author = relationship("Customer", foreign_keys=[author_id])

    def __repr__(self):
        return f"<ForumThread {self.thread_id} - {self.title}>"


class ForumReply(Base):
    __tablename__ = "forum_replies"

    id = Column(Integer, primary_key=True, index=True)
    reply_id = Column(String, unique=True, index=True, nullable=False)

    # Thread
    thread_id = Column(Integer, ForeignKey("forum_threads.id"), nullable=False)

    # Author
    author_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    author_name = Column(String, nullable=False)

    # Reply details
    content = Column(Text, nullable=False)

    # Parent reply (for nested replies)
    parent_reply_id = Column(Integer, ForeignKey("forum_replies.id"), nullable=True)

    # Status
    status = Column(Enum(PostStatus), default=PostStatus.PENDING_APPROVAL)

    # Moderation
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approval_date = Column(DateTime, nullable=True)

    # Flags
    is_accepted_answer = Column(Integer, default=0)  # boolean as int
    is_flagged = Column(Integer, default=0)  # boolean as int

    # Engagement
    like_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)

    # Attachments
    attachments = Column(Text, nullable=True)  # JSON array

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    author = relationship("Customer")

    def __repr__(self):
        return f"<ForumReply {self.reply_id}>"
