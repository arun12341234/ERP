"""
Chatbot Interaction model - AI chatbot and customer support automation.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.config import settings
import enum


class ConversationStatus(str, enum.Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    ABANDONED = "abandoned"


class MessageSender(str, enum.Enum):
    CUSTOMER = "customer"
    BOT = "bot"
    AGENT = "agent"


class IntentCategory(str, enum.Enum):
    PRODUCT_INQUIRY = "product_inquiry"
    ORDER_STATUS = "order_status"
    RETURN_REQUEST = "return_request"
    PAYMENT_ISSUE = "payment_issue"
    SHIPPING_INFO = "shipping_info"
    COMPLAINT = "complaint"
    FEEDBACK = "feedback"
    GENERAL_QUERY = "general_query"
    TECHNICAL_SUPPORT = "technical_support"


class ChatbotConversation(Base):
    __tablename__ = "chatbot_conversations"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, unique=True, index=True, nullable=False)

    # Customer
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    customer_name = Column(String, nullable=True)
    customer_email = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)

    # Session
    session_id = Column(String, index=True, nullable=True)
    channel = Column(String, default="website")  # website, mobile_app, whatsapp, facebook

    # Status
    status = Column(Enum(ConversationStatus), default=ConversationStatus.ACTIVE)

    # Intent detection
    primary_intent = Column(Enum(IntentCategory), nullable=True)
    detected_intents = Column(Text, nullable=True)  # JSON array
    sentiment_score = Column(Integer, nullable=True)  # -100 to +100

    # Escalation
    is_escalated = Column(Integer, default=0)  # boolean as int
    escalated_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    escalation_reason = Column(String, nullable=True)
    escalated_at = Column(DateTime, nullable=True)

    # Resolution
    is_resolved = Column(Integer, default=0)  # boolean as int
    resolution_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    # Rating
    customer_rating = Column(Integer, nullable=True)  # 1-5
    customer_feedback = Column(Text, nullable=True)

    # Metadata
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    language = Column(String, default="en")

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    last_message_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    # Relationships
    customer = relationship("Customer")

    def __repr__(self):
        return f"<ChatbotConversation {self.conversation_id}>"


class ChatbotMessage(Base):
    __tablename__ = "chatbot_messages"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, unique=True, index=True, nullable=False)

    # Conversation
    conversation_id = Column(Integer, ForeignKey("chatbot_conversations.id"), nullable=False)
    session_id = Column(String, index=True, nullable=True)

    # Message details
    sender = Column(Enum(MessageSender), nullable=False)
    message_text = Column(Text, nullable=False)

    # NLP analysis
    detected_intent = Column(String, nullable=True)
    confidence_score = Column(Integer, nullable=True)  # 0-100
    entities_extracted = Column(Text, nullable=True)  # JSON object

    # Response
    bot_response = Column(Text, nullable=True)
    response_template = Column(String, nullable=True)
    kb_article_id = Column(String, nullable=True)  # Knowledge base article reference

    # Attachments
    has_attachments = Column(Integer, default=0)  # boolean as int
    attachments = Column(Text, nullable=True)  # JSON array

    # Quick replies/Buttons
    quick_replies = Column(Text, nullable=True)  # JSON array

    # Metadata
    processing_time_ms = Column(Integer, nullable=True)

    # Timestamps
    sent_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Multi-tenant
    tenant_id = Column(Integer, nullable=True) if settings.ENABLE_TENANCY else None

    def __repr__(self):
        return f"<ChatbotMessage {self.message_id}>"
