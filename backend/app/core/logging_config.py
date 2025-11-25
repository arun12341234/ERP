"""
Logging configuration for the application.
Provides structured logging with file rotation.
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from app.core.config import settings


def setup_logging():
    """Configure application logging with file and console handlers."""

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Root logger configuration
    root_logger = logging.getLogger()

    # Set log level based on environment
    if settings.ENVIRONMENT == "production":
        log_level = logging.INFO
    elif settings.ENVIRONMENT == "staging":
        log_level = logging.INFO
    else:  # development
        log_level = logging.DEBUG

    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers = []

    # Formatter for all handlers
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console Handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File Handler - General Application Logs (rotating by size)
    app_log_file = log_dir / "app.log"
    file_handler = RotatingFileHandler(
        app_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # File Handler - Error Logs (rotating daily)
    error_log_file = log_dir / "error.log"
    error_handler = TimedRotatingFileHandler(
        error_log_file,
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    # File Handler - Access Logs (for API requests)
    access_log_file = log_dir / "access.log"
    access_handler = TimedRotatingFileHandler(
        access_log_file,
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(formatter)

    # Create access logger
    access_logger = logging.getLogger("access")
    access_logger.addHandler(access_handler)
    access_logger.setLevel(logging.INFO)
    access_logger.propagate = False

    # Reduce noise from uvicorn
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)

    logging.info(f"✓ Logging configured for {settings.ENVIRONMENT} environment")
    logging.info(f"✓ Log level: {logging.getLevelName(log_level)}")
    logging.info(f"✓ Logs directory: {log_dir.absolute()}")


# Get loggers for different modules
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module."""
    return logging.getLogger(name)


# Access logger for API requests
access_logger = logging.getLogger("access")
