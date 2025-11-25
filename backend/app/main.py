"""
Main FastAPI application.
Minimal, extensible multi-tenant ERP scaffold.
"""
import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.database import init_db
from app.core.logging_config import setup_logging, access_logger
from app.routers import health, auth, users, items, leads, crm, inventory, manufacturing, finance, logistics, commerce, governance

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all API requests with timing information."""
    start_time = time.time()

    # Get client info
    client_host = request.client.host if request.client else "unknown"

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Log the request
    access_logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Client: {client_host} - "
        f"Time: {process_time:.3f}s"
    )

    # Add processing time to response headers
    response.headers["X-Process-Time"] = str(process_time)

    return response


# Include routers
app.include_router(health.router, prefix=settings.API_V1_STR)

if settings.ENABLE_AUTH:
    app.include_router(auth.router, prefix=settings.API_V1_STR)
    app.include_router(users.router, prefix=settings.API_V1_STR)

app.include_router(items.router, prefix=settings.API_V1_STR)

# CRM & Sales routers
app.include_router(leads.router, prefix=settings.API_V1_STR)
app.include_router(crm.router, prefix=settings.API_V1_STR)

# Inventory & Procurement router
app.include_router(inventory.router, prefix=settings.API_V1_STR)

# Manufacturing & Production router
app.include_router(manufacturing.router, prefix=settings.API_V1_STR)

# Finance & Accounting router
app.include_router(finance.router, prefix=settings.API_V1_STR)

# Supply Chain & Logistics router
app.include_router(logistics.router, prefix=settings.API_V1_STR)

# Omni-Channel Commerce & Digital Engagement router
app.include_router(commerce.router, prefix=settings.API_V1_STR)

# Governance, Audit, AI & System Ops router
app.include_router(governance.router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"📊 Database: {settings.DATABASE_URL}")
    logger.info(f"🔐 Auth: {'Enabled' if settings.ENABLE_AUTH else 'Disabled'}")
    logger.info(f"🏢 Multi-tenancy: {'Enabled' if settings.ENABLE_TENANCY else 'Disabled'}")
    logger.info(f"💳 Subscriptions: {'Enabled' if settings.ENABLE_SUBSCRIPTIONS else 'Disabled'}")
    logger.info(f"🌍 Environment: {settings.ENVIRONMENT}")

    # Create tables
    try:
        init_db()
        logger.info("✓ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        raise


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
    }
