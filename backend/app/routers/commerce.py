"""
Omni-Channel Commerce & Digital Engagement router - Processes 91-100.

This module handles:
- Website Product Listing
- Online Order Processing
- Customer Wallet Management
- Returns Booking
- Loyalty Points
- Offer Campaign Setup
- Marketplace Sync
- Chatbot Interaction
- Community Forum
- Feedback & Rating
"""
from datetime import datetime, date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.core.database import get_db
from app.core.config import settings
from app.models.website_product import WebsiteProduct, ProductVisibility
from app.models.online_order import OnlineOrder, OnlineOrderStatus, PaymentMethod
from app.models.customer_wallet import CustomerWallet, WalletTransaction, WalletTransactionType
from app.models.online_return import OnlineReturn, OnlineReturnStatus
from app.models.loyalty_points import LoyaltyAccount, PointsTransaction, PointsTransactionType
from app.models.offer_campaign import OfferCampaign, CouponUsage, CampaignStatus
from app.models.marketplace_sync import MarketplaceIntegration, MarketplaceListing, SyncStatus
from app.models.chatbot_interaction import ChatbotConversation, ChatbotMessage, ConversationStatus
from app.models.community_forum import ForumThread, ForumReply, PostStatus
from app.models.customer_review import CustomerReview, ReviewStatus
from app.models.audit_log import AuditLog

from app.schemas.commerce import (
    WebsiteProductCreate, WebsiteProductResponse,
    OnlineOrderCreate, OnlineOrderResponse,
    CustomerWalletCreate, CustomerWalletResponse,
    WalletTransactionCreate, WalletTransactionResponse,
    OnlineReturnCreate, OnlineReturnResponse,
    LoyaltyAccountCreate, LoyaltyAccountResponse,
    PointsTransactionCreate, PointsTransactionResponse,
    OfferCampaignCreate, OfferCampaignResponse,
    MarketplaceIntegrationCreate, MarketplaceIntegrationResponse,
    MarketplaceListingCreate, MarketplaceListingResponse,
    ChatbotConversationCreate, ChatbotConversationResponse,
    ChatbotMessageCreate, ChatbotMessageResponse,
    ForumThreadCreate, ForumThreadResponse,
    ForumReplyCreate, ForumReplyResponse,
    CustomerReviewCreate, CustomerReviewResponse,
)

router = APIRouter(prefix="/commerce", tags=["commerce"])


# ============================================================================
# Helper Functions
# ============================================================================

def generate_document_number(prefix: str, db: Session) -> str:
    """Generate unique document number with format PREFIX-YYYY-NNNNN."""
    year = datetime.utcnow().year
    count = db.query(func.count()).filter(
        func.extract('year', WebsiteProduct.created_at) == year
    ).scalar() or 0
    return f"{prefix}-{year}-{count + 1:05d}"


def apply_tenant_filter(query, model, tenant_id: Optional[int] = None):
    """Apply tenant filter if multi-tenancy is enabled."""
    if settings.ENABLE_TENANCY and tenant_id is not None:
        return query.filter(model.tenant_id == tenant_id)
    return query


def create_audit_log(db: Session, entity_type: str, entity_id: int, action: str, user_id: Optional[int] = None):
    """Create audit log entry."""
    log = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        performed_by_id=user_id,
    )
    db.add(log)
    db.commit()


# ============================================================================
# Process 91: Website Product Listing
# ============================================================================

@router.post("/products", response_model=WebsiteProductResponse, status_code=201)
def create_website_product(
    product: WebsiteProductCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a new website product listing."""
    db_product = WebsiteProduct(**product.model_dump())
    if settings.ENABLE_TENANCY:
        db_product.tenant_id = tenant_id

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    create_audit_log(db, "website_product", db_product.id, "created")

    return db_product


@router.get("/products", response_model=List[WebsiteProductResponse])
def list_website_products(
    skip: int = 0,
    limit: int = 100,
    visibility: Optional[str] = None,
    category: Optional[str] = None,
    is_featured: Optional[bool] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List all website products with filters."""
    query = db.query(WebsiteProduct)
    query = apply_tenant_filter(query, WebsiteProduct, tenant_id)

    if visibility:
        query = query.filter(WebsiteProduct.visibility == visibility)
    if category:
        query = query.filter(WebsiteProduct.category == category)
    if is_featured is not None:
        query = query.filter(WebsiteProduct.is_featured == (1 if is_featured else 0))

    return query.offset(skip).limit(limit).all()


@router.put("/products/{product_id}/publish", response_model=WebsiteProductResponse)
def publish_website_product(
    product_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Publish a product to make it visible online."""
    product = db.query(WebsiteProduct).filter(WebsiteProduct.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.visibility = ProductVisibility.PUBLISHED
    product.published_at = datetime.utcnow()
    product.published_by_id = user_id

    db.commit()
    db.refresh(product)

    create_audit_log(db, "website_product", product.id, "published", user_id)

    return product


# ============================================================================
# Process 92: Online Order
# ============================================================================

@router.post("/orders", response_model=OnlineOrderResponse, status_code=201)
def create_online_order(
    order: OnlineOrderCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a new online order from cart checkout."""
    db_order = OnlineOrder(
        order_number=generate_document_number("ORD", db),
        status=OnlineOrderStatus.PENDING_PAYMENT,
        **order.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_order.tenant_id = tenant_id

    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    create_audit_log(db, "online_order", db_order.id, "created")

    return db_order


@router.get("/orders", response_model=List[OnlineOrderResponse])
def list_online_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List all online orders with filters."""
    query = db.query(OnlineOrder)
    query = apply_tenant_filter(query, OnlineOrder, tenant_id)

    if status:
        query = query.filter(OnlineOrder.status == status)
    if customer_id:
        query = query.filter(OnlineOrder.customer_id == customer_id)

    return query.order_by(OnlineOrder.created_at.desc()).offset(skip).limit(limit).all()


@router.put("/orders/{order_id}/confirm-payment", response_model=OnlineOrderResponse)
def confirm_payment(
    order_id: int,
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """Confirm payment for an order."""
    order = db.query(OnlineOrder).filter(OnlineOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = OnlineOrderStatus.PAID
    order.payment_status = "completed"
    order.payment_transaction_id = transaction_id
    order.paid_at = datetime.utcnow()
    order.order_date = datetime.utcnow()

    db.commit()
    db.refresh(order)

    create_audit_log(db, "online_order", order.id, "payment_confirmed")

    return order


# ============================================================================
# Process 93: Customer Wallet
# ============================================================================

@router.post("/wallets", response_model=CustomerWalletResponse, status_code=201)
def create_customer_wallet(
    wallet: CustomerWalletCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a new customer wallet."""
    db_wallet = CustomerWallet(
        wallet_number=generate_document_number("WLT", db),
        **wallet.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_wallet.tenant_id = tenant_id

    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)

    create_audit_log(db, "customer_wallet", db_wallet.id, "created")

    return db_wallet


@router.post("/wallet-transactions", response_model=WalletTransactionResponse, status_code=201)
def create_wallet_transaction(
    transaction: WalletTransactionCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Add funds or debit from customer wallet."""
    wallet = db.query(CustomerWallet).filter(CustomerWallet.id == transaction.wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    # Calculate new balance
    balance_before = wallet.balance
    if transaction.transaction_type == "credit":
        balance_after = balance_before + transaction.amount
    else:  # debit
        if balance_before < transaction.amount:
            raise HTTPException(status_code=400, detail="Insufficient wallet balance")
        balance_after = balance_before - transaction.amount

    # Create transaction
    db_transaction = WalletTransaction(
        transaction_number=generate_document_number("WTX", db),
        balance_before=balance_before,
        balance_after=balance_after,
        **transaction.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_transaction.tenant_id = tenant_id

    # Update wallet balance
    wallet.balance = balance_after
    wallet.last_transaction_at = datetime.utcnow()

    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    create_audit_log(db, "wallet_transaction", db_transaction.id, "created")

    return db_transaction


@router.get("/wallets/customer/{customer_id}", response_model=CustomerWalletResponse)
def get_customer_wallet(customer_id: int, db: Session = Depends(get_db)):
    """Get customer wallet details."""
    wallet = db.query(CustomerWallet).filter(CustomerWallet.customer_id == customer_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet


# ============================================================================
# Process 94: Returns Booking
# ============================================================================

@router.post("/returns", response_model=OnlineReturnResponse, status_code=201)
def create_online_return(
    return_request: OnlineReturnCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a new return request."""
    db_return = OnlineReturn(
        return_number=generate_document_number("RET", db),
        **return_request.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_return.tenant_id = tenant_id

    db.add(db_return)
    db.commit()
    db.refresh(db_return)

    create_audit_log(db, "online_return", db_return.id, "created")

    return db_return


@router.put("/returns/{return_id}/approve", response_model=OnlineReturnResponse)
def approve_return(
    return_id: int,
    user_id: int,
    approval_notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Approve a return request."""
    db_return = db.query(OnlineReturn).filter(OnlineReturn.id == return_id).first()
    if not db_return:
        raise HTTPException(status_code=404, detail="Return not found")

    db_return.status = OnlineReturnStatus.APPROVED
    db_return.approved_by_id = user_id
    db_return.approval_date = datetime.utcnow()
    db_return.approval_notes = approval_notes

    db.commit()
    db.refresh(db_return)

    create_audit_log(db, "online_return", db_return.id, "approved", user_id)

    return db_return


@router.get("/returns", response_model=List[OnlineReturnResponse])
def list_returns(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List all returns with filters."""
    query = db.query(OnlineReturn)
    query = apply_tenant_filter(query, OnlineReturn, tenant_id)

    if status:
        query = query.filter(OnlineReturn.status == status)
    if customer_id:
        query = query.filter(OnlineReturn.customer_id == customer_id)

    return query.offset(skip).limit(limit).all()


# ============================================================================
# Process 95: Loyalty Points
# ============================================================================

@router.post("/loyalty-accounts", response_model=LoyaltyAccountResponse, status_code=201)
def create_loyalty_account(
    account: LoyaltyAccountCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a new loyalty account for a customer."""
    db_account = LoyaltyAccount(
        account_number=generate_document_number("LOY", db),
        **account.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_account.tenant_id = tenant_id

    db.add(db_account)
    db.commit()
    db.refresh(db_account)

    create_audit_log(db, "loyalty_account", db_account.id, "created")

    return db_account


@router.post("/points-transactions", response_model=PointsTransactionResponse, status_code=201)
def add_points_transaction(
    transaction: PointsTransactionCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Add or redeem loyalty points."""
    account = db.query(LoyaltyAccount).filter(LoyaltyAccount.id == transaction.loyalty_account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Loyalty account not found")

    # Calculate new balance
    balance_before = account.points_balance
    if transaction.transaction_type == "earned":
        balance_after = balance_before + transaction.points
        account.lifetime_points_earned += transaction.points
    else:  # redeemed
        if balance_before < transaction.points:
            raise HTTPException(status_code=400, detail="Insufficient points balance")
        balance_after = balance_before - transaction.points
        account.lifetime_points_redeemed += transaction.points

    # Create transaction
    db_transaction = PointsTransaction(
        transaction_number=generate_document_number("PTX", db),
        balance_before=balance_before,
        balance_after=balance_after,
        **transaction.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_transaction.tenant_id = tenant_id

    # Update account balance
    account.points_balance = balance_after
    account.last_activity_date = date.today()

    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    create_audit_log(db, "points_transaction", db_transaction.id, "created")

    return db_transaction


@router.get("/loyalty-accounts/customer/{customer_id}", response_model=LoyaltyAccountResponse)
def get_loyalty_account(customer_id: int, db: Session = Depends(get_db)):
    """Get customer loyalty account."""
    account = db.query(LoyaltyAccount).filter(LoyaltyAccount.customer_id == customer_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Loyalty account not found")
    return account


# ============================================================================
# Process 96: Offer Campaign Setup
# ============================================================================

@router.post("/campaigns", response_model=OfferCampaignResponse, status_code=201)
def create_offer_campaign(
    campaign: OfferCampaignCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a new promotional campaign."""
    db_campaign = OfferCampaign(**campaign.model_dump())
    if settings.ENABLE_TENANCY:
        db_campaign.tenant_id = tenant_id

    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)

    create_audit_log(db, "offer_campaign", db_campaign.id, "created")

    return db_campaign


@router.put("/campaigns/{campaign_id}/publish", response_model=OfferCampaignResponse)
def publish_campaign(
    campaign_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Publish an offer campaign."""
    campaign = db.query(OfferCampaign).filter(OfferCampaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    campaign.status = CampaignStatus.ACTIVE
    campaign.is_published = 1
    campaign.published_at = datetime.utcnow()
    campaign.published_by_id = user_id

    db.commit()
    db.refresh(campaign)

    create_audit_log(db, "offer_campaign", campaign.id, "published", user_id)

    return campaign


@router.get("/campaigns", response_model=List[OfferCampaignResponse])
def list_campaigns(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    is_published: Optional[bool] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List all promotional campaigns."""
    query = db.query(OfferCampaign)
    query = apply_tenant_filter(query, OfferCampaign, tenant_id)

    if status:
        query = query.filter(OfferCampaign.status == status)
    if is_published is not None:
        query = query.filter(OfferCampaign.is_published == (1 if is_published else 0))

    return query.offset(skip).limit(limit).all()


# ============================================================================
# Process 97: Marketplace Sync
# ============================================================================

@router.post("/marketplace-integrations", response_model=MarketplaceIntegrationResponse, status_code=201)
def create_marketplace_integration(
    integration: MarketplaceIntegrationCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Register a marketplace integration."""
    db_integration = MarketplaceIntegration(**integration.model_dump())
    if settings.ENABLE_TENANCY:
        db_integration.tenant_id = tenant_id

    db.add(db_integration)
    db.commit()
    db.refresh(db_integration)

    create_audit_log(db, "marketplace_integration", db_integration.id, "created")

    return db_integration


@router.post("/marketplace-listings", response_model=MarketplaceListingResponse, status_code=201)
def create_marketplace_listing(
    listing: MarketplaceListingCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a product listing on marketplace."""
    db_listing = MarketplaceListing(
        listing_id=generate_document_number("MPL", db),
        **listing.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_listing.tenant_id = tenant_id

    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)

    create_audit_log(db, "marketplace_listing", db_listing.id, "created")

    return db_listing


@router.put("/marketplace-integrations/{integration_id}/sync", response_model=MarketplaceIntegrationResponse)
def sync_marketplace(
    integration_id: int,
    db: Session = Depends(get_db)
):
    """Synchronize data with marketplace."""
    integration = db.query(MarketplaceIntegration).filter(MarketplaceIntegration.id == integration_id).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")

    integration.sync_status = SyncStatus.SYNCING
    integration.last_sync_timestamp = datetime.utcnow()
    integration.last_sync_message = "Sync initiated"

    # In production, this would call the actual marketplace API

    integration.sync_status = SyncStatus.SYNCED

    db.commit()
    db.refresh(integration)

    create_audit_log(db, "marketplace_integration", integration.id, "synced")

    return integration


@router.get("/marketplace-listings", response_model=List[MarketplaceListingResponse])
def list_marketplace_listings(
    skip: int = 0,
    limit: int = 100,
    platform: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List marketplace listings."""
    query = db.query(MarketplaceListing)
    query = apply_tenant_filter(query, MarketplaceListing, tenant_id)

    if platform:
        query = query.filter(MarketplaceListing.platform == platform)

    return query.offset(skip).limit(limit).all()


# ============================================================================
# Process 98: Chatbot Interaction
# ============================================================================

@router.post("/chatbot/conversations", response_model=ChatbotConversationResponse, status_code=201)
def create_chatbot_conversation(
    conversation: ChatbotConversationCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Start a new chatbot conversation."""
    db_conversation = ChatbotConversation(
        conversation_id=generate_document_number("CHAT", db),
        **conversation.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_conversation.tenant_id = tenant_id

    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)

    return db_conversation


@router.post("/chatbot/messages", response_model=ChatbotMessageResponse, status_code=201)
def create_chatbot_message(
    message: ChatbotMessageCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Add a message to chatbot conversation."""
    db_message = ChatbotMessage(
        message_id=generate_document_number("MSG", db),
        **message.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_message.tenant_id = tenant_id

    # Update conversation's last message time
    conversation = db.query(ChatbotConversation).filter(
        ChatbotConversation.id == message.conversation_id
    ).first()
    if conversation:
        conversation.last_message_at = datetime.utcnow()

    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    return db_message


@router.get("/chatbot/conversations/{conversation_id}/messages", response_model=List[ChatbotMessageResponse])
def get_conversation_messages(conversation_id: int, db: Session = Depends(get_db)):
    """Get all messages in a conversation."""
    messages = db.query(ChatbotMessage).filter(
        ChatbotMessage.conversation_id == conversation_id
    ).order_by(ChatbotMessage.sent_at.asc()).all()

    return messages


# ============================================================================
# Process 99: Community Forum Post
# ============================================================================

@router.post("/forum/threads", response_model=ForumThreadResponse, status_code=201)
def create_forum_thread(
    thread: ForumThreadCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a new forum thread."""
    db_thread = ForumThread(
        thread_id=generate_document_number("THR", db),
        **thread.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_thread.tenant_id = tenant_id

    db.add(db_thread)
    db.commit()
    db.refresh(db_thread)

    create_audit_log(db, "forum_thread", db_thread.id, "created")

    return db_thread


@router.put("/forum/threads/{thread_id}/approve", response_model=ForumThreadResponse)
def approve_forum_thread(
    thread_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Approve a forum thread for publication."""
    thread = db.query(ForumThread).filter(ForumThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    thread.status = PostStatus.APPROVED
    thread.approved_by_id = user_id
    thread.approval_date = datetime.utcnow()

    db.commit()
    db.refresh(thread)

    create_audit_log(db, "forum_thread", thread.id, "approved", user_id)

    return thread


@router.post("/forum/replies", response_model=ForumReplyResponse, status_code=201)
def create_forum_reply(
    reply: ForumReplyCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Create a reply to a forum thread."""
    db_reply = ForumReply(
        reply_id=generate_document_number("RPL", db),
        **reply.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_reply.tenant_id = tenant_id

    # Update thread reply count
    thread = db.query(ForumThread).filter(ForumThread.id == reply.thread_id).first()
    if thread:
        thread.reply_count += 1
        thread.last_activity_at = datetime.utcnow()
        thread.last_reply_by_id = reply.author_id

    db.add(db_reply)
    db.commit()
    db.refresh(db_reply)

    create_audit_log(db, "forum_reply", db_reply.id, "created")

    return db_reply


@router.get("/forum/threads", response_model=List[ForumThreadResponse])
def list_forum_threads(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List forum threads."""
    query = db.query(ForumThread)
    query = apply_tenant_filter(query, ForumThread, tenant_id)

    if category:
        query = query.filter(ForumThread.category == category)
    if status:
        query = query.filter(ForumThread.status == status)

    return query.order_by(ForumThread.last_activity_at.desc()).offset(skip).limit(limit).all()


# ============================================================================
# Process 100: Feedback & Rating
# ============================================================================

@router.post("/reviews", response_model=CustomerReviewResponse, status_code=201)
def create_customer_review(
    review: CustomerReviewCreate,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """Submit a product review."""
    db_review = CustomerReview(
        review_id=generate_document_number("REV", db),
        **review.model_dump()
    )
    if settings.ENABLE_TENANCY:
        db_review.tenant_id = tenant_id

    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    create_audit_log(db, "customer_review", db_review.id, "created")

    return db_review


@router.put("/reviews/{review_id}/approve", response_model=CustomerReviewResponse)
def approve_review(
    review_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Approve a customer review for publication."""
    review = db.query(CustomerReview).filter(CustomerReview.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    review.status = ReviewStatus.APPROVED
    review.moderated_by_id = user_id
    review.moderation_date = datetime.utcnow()

    db.commit()
    db.refresh(review)

    create_audit_log(db, "customer_review", review.id, "approved", user_id)

    return review


@router.get("/reviews", response_model=List[CustomerReviewResponse])
def list_reviews(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None,
    status: Optional[str] = None,
    min_rating: Optional[int] = None,
    db: Session = Depends(get_db),
    tenant_id: Optional[int] = None
):
    """List customer reviews with filters."""
    query = db.query(CustomerReview)
    query = apply_tenant_filter(query, CustomerReview, tenant_id)

    if product_id:
        query = query.filter(CustomerReview.product_id == product_id)
    if status:
        query = query.filter(CustomerReview.status == status)
    if min_rating:
        query = query.filter(CustomerReview.overall_rating >= min_rating)

    return query.order_by(CustomerReview.review_date.desc()).offset(skip).limit(limit).all()


@router.get("/reviews/product/{product_id}/stats")
def get_product_review_stats(product_id: int, db: Session = Depends(get_db)):
    """Get review statistics for a product."""
    reviews = db.query(CustomerReview).filter(
        CustomerReview.product_id == product_id,
        CustomerReview.status == ReviewStatus.APPROVED
    ).all()

    if not reviews:
        return {
            "total_reviews": 0,
            "average_rating": 0.0,
            "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        }

    total = len(reviews)
    avg_rating = sum(r.overall_rating for r in reviews) / total
    distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for review in reviews:
        distribution[review.overall_rating] += 1

    return {
        "total_reviews": total,
        "average_rating": round(avg_rating, 2),
        "rating_distribution": distribution
    }
