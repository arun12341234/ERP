"""Health check endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/healthz")
def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "features": {
            "auth": settings.ENABLE_AUTH,
            "tenancy": settings.ENABLE_TENANCY,
            "subscriptions": settings.ENABLE_SUBSCRIPTIONS,
        }
    }


@router.get("/healthz/db")
def health_check_db(db: Session = Depends(get_db)):
    """Database health check."""
    try:
        # Simple query to check DB connection
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
