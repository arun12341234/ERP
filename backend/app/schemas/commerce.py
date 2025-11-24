"""
Pydantic schemas for Omni-Channel Commerce & Digital Engagement module.
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field


# ============================================================================
# Process 91: Website Product Listing
# ============================================================================

class WebsiteProductCreate(BaseModel):
    sku: str
    product_id: Optional[int] = None
    title: str
    slug: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    price: int = 0  # in cents
    compare_at_price: Optional[int] = None
    stock_quantity: float = 0.0
    category: Optional[str] = None
    tags: Optional[str] = None  # JSON array
    featured_image: Optional[str] = None
    visibility: str = "draft"


class WebsiteProductResponse(BaseModel):
    id: int
    sku: str
    product_id: Optional[int]
    title: str
    slug: str
    short_description: Optional[str]
    long_description: Optional[str]
    price: int
    compare_at_price: Optional[int]
    cost_per_item: Optional[int]
    stock_quantity: float
    low_stock_threshold: float
    track_inventory: int
    meta_title: Optional[str]
    meta_description: Optional[str]
    featured_image: Optional[str]
    gallery_images: Optional[str]
    category: Optional[str]
    tags: Optional[str]
    brand: Optional[str]
    visibility: str
    is_featured: int
    is_new_arrival: int
    is_best_seller: int
    published_at: Optional[datetime]
    view_count: int
    order_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 92: Online Order
# ============================================================================

class OnlineOrderCreate(BaseModel):
    customer_id: int
    customer_email: str
    customer_phone: Optional[str] = None
    items: str  # JSON array
    shipping_address_line1: str
    shipping_city: str
    shipping_state: str
    shipping_postal_code: str
    shipping_country: str = "India"
    payment_method: Optional[str] = None


class OnlineOrderResponse(BaseModel):
    id: int
    order_number: str
    customer_id: int
    customer_email: str
    customer_phone: Optional[str]
    status: str
    order_date: Optional[datetime]
    items: str
    subtotal: int
    shipping_charges: int
    tax_amount: int
    discount_amount: int
    total_amount: int
    coupon_code: Optional[str]
    loyalty_points_used: int
    payment_method: Optional[str]
    payment_status: str
    payment_transaction_id: Optional[str]
    paid_at: Optional[datetime]
    shipping_name: Optional[str]
    shipping_address_line1: Optional[str]
    shipping_city: Optional[str]
    shipping_state: Optional[str]
    shipping_postal_code: Optional[str]
    tracking_number: Optional[str]
    shipped_at: Optional[datetime]
    delivered_at: Optional[datetime]
    source_channel: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 93: Customer Wallet
# ============================================================================

class CustomerWalletCreate(BaseModel):
    customer_id: int


class CustomerWalletResponse(BaseModel):
    id: int
    wallet_number: str
    customer_id: int
    balance: int
    credit_limit: int
    is_active: int
    is_locked: int
    last_transaction_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WalletTransactionCreate(BaseModel):
    wallet_id: int
    customer_id: int
    transaction_type: str  # credit or debit
    transaction_source: str
    amount: int  # in cents
    description: Optional[str] = None
    payment_method: Optional[str] = None
    payment_transaction_id: Optional[str] = None


class WalletTransactionResponse(BaseModel):
    id: int
    transaction_number: str
    wallet_id: int
    customer_id: int
    transaction_type: str
    transaction_source: str
    amount: int
    balance_before: int
    balance_after: int
    reference_type: Optional[str]
    reference_id: Optional[int]
    reference_number: Optional[str]
    payment_method: Optional[str]
    payment_transaction_id: Optional[str]
    payment_status: str
    description: Optional[str]
    transaction_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 94: Returns Booking
# ============================================================================

class OnlineReturnCreate(BaseModel):
    online_order_id: int
    order_number: str
    customer_id: int
    request_date: date
    return_reason: str
    reason_description: Optional[str] = None
    items: str  # JSON array
    total_quantity: float
    pickup_address: Optional[str] = None


class OnlineReturnResponse(BaseModel):
    id: int
    return_number: str
    online_order_id: int
    order_number: str
    customer_id: int
    request_date: date
    return_reason: str
    reason_description: Optional[str]
    items: str
    total_quantity: float
    quantity_received: float
    status: str
    approved_by_id: Optional[int]
    approval_date: Optional[datetime]
    approval_notes: Optional[str]
    pickup_date: Optional[date]
    pickup_address: Optional[str]
    pickup_tracking_number: Optional[str]
    inspected_by_id: Optional[int]
    inspection_date: Optional[datetime]
    inspection_notes: Optional[str]
    condition_on_return: Optional[str]
    refund_method: Optional[str]
    refund_amount: int
    refund_processed: int
    refund_transaction_id: Optional[str]
    refunded_at: Optional[datetime]
    is_exchange: int
    exchange_order_id: Optional[int]
    images: Optional[str]
    customer_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 95: Loyalty Points
# ============================================================================

class LoyaltyAccountCreate(BaseModel):
    customer_id: int


class LoyaltyAccountResponse(BaseModel):
    id: int
    account_number: str
    customer_id: int
    points_balance: int
    lifetime_points_earned: int
    lifetime_points_redeemed: int
    current_tier: str
    tier_since: Optional[date]
    is_active: int
    enrollment_date: date
    last_activity_date: Optional[date]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PointsTransactionCreate(BaseModel):
    loyalty_account_id: int
    customer_id: int
    transaction_type: str  # earned or redeemed
    points_source: Optional[str] = None
    points: int
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    reference_number: Optional[str] = None
    description: Optional[str] = None


class PointsTransactionResponse(BaseModel):
    id: int
    transaction_number: str
    loyalty_account_id: int
    customer_id: int
    transaction_type: str
    points_source: Optional[str]
    points: int
    balance_before: int
    balance_after: int
    reference_type: Optional[str]
    reference_id: Optional[int]
    reference_number: Optional[str]
    expires_at: Optional[date]
    is_expired: int
    points_multiplier: int
    description: Optional[str]
    transaction_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 96: Offer Campaign Setup
# ============================================================================

class OfferCampaignCreate(BaseModel):
    campaign_code: str
    campaign_name: str
    campaign_type: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    discount_percentage: Optional[float] = None
    discount_amount: Optional[int] = None
    minimum_purchase_amount: int = 0
    coupon_code: Optional[str] = None
    is_coupon_required: int = 1


class OfferCampaignResponse(BaseModel):
    id: int
    campaign_code: str
    campaign_name: str
    campaign_type: str
    description: Optional[str]
    status: str
    start_date: datetime
    end_date: datetime
    discount_percentage: Optional[float]
    discount_amount: Optional[int]
    minimum_purchase_amount: int
    maximum_discount_amount: Optional[int]
    buy_quantity: Optional[int]
    get_quantity: Optional[int]
    cashback_percentage: Optional[float]
    cashback_amount: Optional[int]
    loyalty_points_multiplier: int
    applies_to: str
    product_ids: Optional[str]
    category_names: Optional[str]
    usage_limit_total: Optional[int]
    usage_limit_per_customer: int
    usage_count: int
    customer_segment: Optional[str]
    is_coupon_required: int
    coupon_code: Optional[str]
    auto_apply: int
    is_published: int
    published_at: Optional[datetime]
    conversion_count: int
    total_discount_given: int
    total_revenue: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 97: Marketplace Sync
# ============================================================================

class MarketplaceIntegrationCreate(BaseModel):
    integration_code: str
    platform: str
    platform_store_name: Optional[str] = None
    api_key: Optional[str] = None
    seller_id: Optional[str] = None
    sync_frequency_minutes: int = 60


class MarketplaceIntegrationResponse(BaseModel):
    id: int
    integration_code: str
    platform: str
    platform_store_name: Optional[str]
    seller_id: Optional[str]
    is_active: int
    sync_status: str
    auto_sync_enabled: int
    sync_frequency_minutes: int
    last_sync_timestamp: Optional[datetime]
    last_sync_message: Optional[str]
    sync_inventory: int
    sync_prices: int
    sync_orders: int
    price_markup_percentage: float
    price_markup_amount: int
    commission_percentage: float
    fixed_fee_per_order: int
    contact_person: Optional[str]
    contact_email: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MarketplaceListingCreate(BaseModel):
    integration_id: int
    platform: str
    product_id: Optional[int] = None
    website_product_id: Optional[int] = None
    marketplace_sku: str
    title: str
    description: Optional[str] = None
    price: int = 0
    quantity: float = 0.0


class MarketplaceListingResponse(BaseModel):
    id: int
    listing_id: str
    integration_id: int
    platform: str
    product_id: Optional[int]
    website_product_id: Optional[int]
    marketplace_product_id: Optional[str]
    marketplace_sku: Optional[str]
    title: str
    description: Optional[str]
    category: Optional[str]
    price: int
    compare_at_price: Optional[int]
    quantity: float
    low_stock_threshold: float
    listing_status: str
    sync_status: str
    last_synced_at: Optional[datetime]
    sync_error_message: Optional[str]
    images: Optional[str]
    attributes: Optional[str]
    view_count: int
    order_count: int
    total_revenue: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 98: Chatbot Interaction
# ============================================================================

class ChatbotConversationCreate(BaseModel):
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    channel: str = "website"
    session_id: Optional[str] = None


class ChatbotConversationResponse(BaseModel):
    id: int
    conversation_id: str
    customer_id: Optional[int]
    customer_name: Optional[str]
    customer_email: Optional[str]
    session_id: Optional[str]
    channel: str
    status: str
    primary_intent: Optional[str]
    detected_intents: Optional[str]
    sentiment_score: Optional[int]
    is_escalated: int
    escalated_to_id: Optional[int]
    escalation_reason: Optional[str]
    escalated_at: Optional[datetime]
    is_resolved: int
    resolution_notes: Optional[str]
    resolved_at: Optional[datetime]
    customer_rating: Optional[int]
    customer_feedback: Optional[str]
    language: str
    started_at: datetime
    last_message_at: datetime
    ended_at: Optional[datetime]

    class Config:
        from_attributes = True


class ChatbotMessageCreate(BaseModel):
    conversation_id: int
    session_id: Optional[str] = None
    sender: str  # customer, bot, agent
    message_text: str
    detected_intent: Optional[str] = None
    confidence_score: Optional[int] = None


class ChatbotMessageResponse(BaseModel):
    id: int
    message_id: str
    conversation_id: int
    session_id: Optional[str]
    sender: str
    message_text: str
    detected_intent: Optional[str]
    confidence_score: Optional[int]
    entities_extracted: Optional[str]
    bot_response: Optional[str]
    response_template: Optional[str]
    kb_article_id: Optional[str]
    has_attachments: int
    attachments: Optional[str]
    quick_replies: Optional[str]
    processing_time_ms: Optional[int]
    sent_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 99: Community Forum Post
# ============================================================================

class ForumThreadCreate(BaseModel):
    author_id: int
    author_name: str
    title: str
    slug: str
    content: str
    category: str
    post_type: str = "discussion"
    tags: Optional[str] = None


class ForumThreadResponse(BaseModel):
    id: int
    thread_id: str
    author_id: int
    author_name: str
    title: str
    slug: str
    content: str
    category: str
    post_type: str
    tags: Optional[str]
    status: str
    approved_by_id: Optional[int]
    approval_date: Optional[datetime]
    rejection_reason: Optional[str]
    is_pinned: int
    is_locked: int
    is_featured: int
    view_count: int
    reply_count: int
    like_count: int
    share_count: int
    has_accepted_answer: int
    accepted_answer_id: Optional[int]
    last_activity_at: datetime
    last_reply_by_id: Optional[int]
    attachments: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ForumReplyCreate(BaseModel):
    thread_id: int
    author_id: int
    author_name: str
    content: str
    parent_reply_id: Optional[int] = None


class ForumReplyResponse(BaseModel):
    id: int
    reply_id: str
    thread_id: int
    author_id: int
    author_name: str
    content: str
    parent_reply_id: Optional[int]
    status: str
    approved_by_id: Optional[int]
    approval_date: Optional[datetime]
    is_accepted_answer: int
    is_flagged: int
    like_count: int
    helpful_count: int
    attachments: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Process 100: Feedback & Rating
# ============================================================================

class CustomerReviewCreate(BaseModel):
    product_id: Optional[int] = None
    website_product_id: Optional[int] = None
    customer_id: int
    customer_name: str
    customer_email: Optional[str] = None
    online_order_id: Optional[int] = None
    overall_rating: int  # 1-5
    review_title: Optional[str] = None
    review_text: str
    would_recommend: Optional[int] = None


class CustomerReviewResponse(BaseModel):
    id: int
    review_id: str
    product_id: Optional[int]
    website_product_id: Optional[int]
    customer_id: int
    customer_name: str
    customer_email: Optional[str]
    online_order_id: Optional[int]
    is_verified_purchase: int
    overall_rating: int
    quality_rating: Optional[int]
    value_rating: Optional[int]
    delivery_rating: Optional[int]
    review_title: Optional[str]
    review_text: str
    pros: Optional[str]
    cons: Optional[str]
    images: Optional[str]
    videos: Optional[str]
    would_recommend: Optional[int]
    status: str
    moderated_by_id: Optional[int]
    moderation_date: Optional[datetime]
    moderation_notes: Optional[str]
    is_featured: int
    is_flagged: int
    flag_count: int
    helpful_count: int
    not_helpful_count: int
    seller_response: Optional[str]
    seller_response_date: Optional[datetime]
    review_source: str
    loyalty_points_awarded: int
    review_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
