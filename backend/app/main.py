"""
Main FastAPI application.
Minimal, extensible multi-tenant ERP scaffold.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.routers import health, auth, users, items, leads, crm, inventory

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    print(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"📊 Database: {settings.DATABASE_URL}")
    print(f"🔐 Auth: {'Enabled' if settings.ENABLE_AUTH else 'Disabled'}")
    print(f"🏢 Multi-tenancy: {'Enabled' if settings.ENABLE_TENANCY else 'Disabled'}")
    print(f"💳 Subscriptions: {'Enabled' if settings.ENABLE_SUBSCRIPTIONS else 'Disabled'}")

    # Create tables
    init_db()


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
    }
