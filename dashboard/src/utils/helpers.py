"""
Helper Functions

Common utility functions used across the sensors dashboard application.
"""

from datetime import datetime
from typing import Optional, Tuple, Any
import pytz
from src.utils.config import Config


def format_timestamp(
    timestamp: datetime,
    timezone: str = None,
    format_string: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """
    Format a timestamp for display
    
    Args:
        timestamp: Datetime object to format
        timezone: Target timezone (defaults to config default)
        format_string: Format string for output
        
    Returns:
        Formatted timestamp string
    """
    if timezone is None:
        timezone = Config.DEFAULT_TIMEZONE
    
    # Convert to target timezone if needed
    if timestamp.tzinfo is None:
        # Assume UTC if no timezone info
        timestamp = pytz.UTC.localize(timestamp)
    
    target_tz = pytz.timezone(timezone)
    localized_timestamp = timestamp.astimezone(target_tz)
    
    return localized_timestamp.strftime(format_string)


def validate_date_range(
    start_date: datetime,
    end_date: datetime,
    max_days: int = 365
) -> Tuple[bool, Optional[str]]:
    """
    Validate a date range for data queries
    
    Args:
        start_date: Start of date range
        end_date: End of date range
        max_days: Maximum allowed range in days
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if start is before or equal to end (allow single day selection)
    if start_date > end_date:
        return False, "Start date must be before or equal to end date"
    
    # Check if range is not too large
    date_diff = end_date - start_date
    if date_diff.days > max_days:
        return False, f"Date range cannot exceed {max_days} days"
    
    # Check if dates are not in the future
    now = datetime.now(pytz.UTC)
    
    # Make end_date timezone-aware if it isn't already
    if end_date.tzinfo is None:
        end_date = pytz.UTC.localize(end_date)
    
    if end_date > now:
        return False, "End date cannot be in the future"
    
    return True, None


def convert_timezone(
    timestamp: datetime,
    from_tz: str,
    to_tz: str
) -> datetime:
    """
    Convert timestamp between timezones
    
    Args:
        timestamp: Timestamp to convert
        from_tz: Source timezone
        to_tz: Target timezone
        
    Returns:
        Converted timestamp
    """
    from_timezone = pytz.timezone(from_tz)
    to_timezone = pytz.timezone(to_tz)
    
    # Localize if naive
    if timestamp.tzinfo is None:
        timestamp = from_timezone.localize(timestamp)
    
    return timestamp.astimezone(to_timezone)


def safe_float_conversion(value: Any, default: float = 0.0) -> float:
    """
    Safely convert a value to float
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Float value or default
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def calculate_data_points_limit(time_range_days: int) -> int:
    """
    Calculate appropriate data points limit based on time range
    
    Args:
        time_range_days: Number of days in the query range
        
    Returns:
        Recommended data points limit
    """
    if time_range_days <= 1:
        return 1440  # 1 point per minute for 1 day
    elif time_range_days <= 7:
        return 2016  # 1 point per 5 minutes for 1 week
    elif time_range_days <= 30:
        return 1440  # 1 point per 30 minutes for 1 month
    else:
        return 720   # 1 point per hour for longer periods


def get_aggregation_method(time_range_days: int) -> str:
    """
    Get recommended aggregation method based on time range
    
    Args:
        time_range_days: Number of days in the query range
        
    Returns:
        Recommended aggregation method
    """
    if time_range_days <= 1:
        return Config.AGGREGATION_METHODS['interpolation']
    elif time_range_days <= 7:
        return Config.AGGREGATION_METHODS['interpolation']
    elif time_range_days <= 30:
        return Config.AGGREGATION_METHODS['hourly']
    else:
        return Config.AGGREGATION_METHODS['daily']


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}" 