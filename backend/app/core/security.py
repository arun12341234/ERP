"""
Security utilities: password hashing, JWT token management.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token."""
    import logging
    logger = logging.getLogger(__name__)

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        logger.debug(f"Token decoded successfully, payload keys: {payload.keys()}")
        return payload
    except JWTError as e:
        logger.error(f"JWT decode error: {str(e)}, token length: {len(token) if token else 0}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {str(e)}")
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get current authenticated user from JWT token."""
    from app.models.user import User
    import logging

    logger = logging.getLogger(__name__)

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        if payload is None:
            logger.error("Token decode failed - payload is None")
            raise credentials_exception

        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            logger.error("No 'sub' field in token payload")
            raise credentials_exception

        # Convert to int if it's a string
        try:
            user_id = int(user_id_raw)
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid user_id in token: {user_id_raw}, error: {e}")
            raise credentials_exception

        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            logger.error(f"User not found with id: {user_id}")
            raise credentials_exception

        # If tenancy is enabled, add tenant_id to user context
        if settings.ENABLE_TENANCY and payload.get("tenant_id"):
            user.current_tenant_id = payload.get("tenant_id")

        logger.info(f"User authenticated successfully: {user.email}")
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {e}")
        raise credentials_exception


def get_current_active_user(current_user = Depends(get_current_user)):
    """Ensure user is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_admin(current_user = Depends(get_current_active_user)):
    """Require admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
