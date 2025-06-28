"""
Logging Setup System

Configures structured logging for the sensors dashboard application
with appropriate log levels and formatting.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Set up logging configuration for the sensors dashboard
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs to
        format_string: Optional custom format string
        
    Returns:
        Configured logger instance
    """
    
    # Default format string
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )
    
    # Configure logging level
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger("sensors_dashboard")
    logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(format_string)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    logger.info(f"Logging initialized - Level: {level}")
    if log_file:
        logger.info(f"Logging to file: {log_file}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module
    
    Args:
        name: Module name for the logger
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"sensors_dashboard.{name}")


# Module-specific loggers
def get_data_logger() -> logging.Logger:
    """Get logger for data processing modules"""
    return get_logger("data")


def get_ui_logger() -> logging.Logger:
    """Get logger for UI modules"""
    return get_logger("ui")


def get_cache_logger() -> logging.Logger:
    """Get logger for cache modules"""
    return get_logger("cache")


def get_utils_logger() -> logging.Logger:
    """Get logger for utility modules"""
    return get_logger("utils") 