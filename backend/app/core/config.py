"""
Configuration management using pydantic-settings.
All settings can be overridden via environment variables.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Multi-Tenant ERP"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"  # development, staging, production

    # Database
    DATABASE_URL: str = "sqlite:///./erp.db"

    # Security
    SECRET_KEY: str = "change-this-to-a-random-secret-key-min-32-characters"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Features (toggleable)
    ENABLE_AUTH: bool = True
    ENABLE_TENANCY: bool = False
    ENABLE_SUBSCRIPTIONS: bool = False

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Admin
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "admin123"

    class Config:
        env_file = ".env"
        case_sensitive = True

    def validate_production_config(self):
        """Validate that production settings are properly configured."""
        if self.ENVIRONMENT == "production":
            errors = []

            # Check SECRET_KEY
            if "change-this" in self.SECRET_KEY.lower() or len(self.SECRET_KEY) < 32:
                errors.append("SECRET_KEY must be changed and at least 32 characters for production")

            # Check admin password
            if self.ADMIN_PASSWORD in ["admin123", "password", "123456"]:
                errors.append("ADMIN_PASSWORD must be changed from default value")

            # Check database
            if "sqlite" in self.DATABASE_URL.lower():
                errors.append("SQLite is not recommended for production. Use PostgreSQL.")

            # Check CORS
            if any("localhost" in origin for origin in self.CORS_ORIGINS):
                errors.append("CORS_ORIGINS contains localhost. Update for production domain.")

            if errors:
                error_msg = "\n".join([f"  - {err}" for err in errors])
                raise ValueError(f"\n❌ PRODUCTION CONFIGURATION ERRORS:\n{error_msg}\n")

        return True


settings = Settings()

# Validate production config on startup
if settings.ENVIRONMENT == "production":
    settings.validate_production_config()
