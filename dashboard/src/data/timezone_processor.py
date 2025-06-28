"""
Timezone Processing Module

Handles timezone conversions between Pacific/Auckland and UTC with proper
daylight saving time (DST) handling as designed in the creative phase.
"""

import pytz
from datetime import datetime
from typing import Union
import pandas as pd
from src.utils.config import Config
from src.utils.logging_setup import get_data_logger

logger = get_data_logger()


class TimezoneProcessor:
    """
    Timezone processor for Pacific/Auckland ↔ UTC conversions
    
    Implements timezone handling from the Hybrid Cached Pipeline Architecture
    with proper DST transition handling and performance optimization.
    """
    
    def __init__(self):
        """Initialize timezone processor with Pacific/Auckland and UTC timezones"""
        self.local_tz = pytz.timezone(Config.DEFAULT_TIMEZONE)  # Pacific/Auckland
        self.utc_tz = pytz.timezone(Config.UTC_TIMEZONE)  # UTC
        
        logger.info(f"Timezone processor initialized - Local: {Config.DEFAULT_TIMEZONE}, UTC: {Config.UTC_TIMEZONE}")
    
    def utc_to_local(self, utc_datetime: Union[datetime, str, pd.Timestamp]) -> datetime:
        """
        Convert UTC datetime to Pacific/Auckland timezone
        
        Args:
            utc_datetime: UTC datetime (datetime, ISO string, or pandas Timestamp)
            
        Returns:
            Localized datetime in Pacific/Auckland timezone
        """
        try:
            # Convert input to datetime if string
            if isinstance(utc_datetime, str):
                dt = pd.to_datetime(utc_datetime)
            elif isinstance(utc_datetime, pd.Timestamp):
                dt = utc_datetime.to_pydatetime()
            else:
                dt = utc_datetime
            
            # Ensure datetime is UTC aware
            if dt.tzinfo is None:
                dt = self.utc_tz.localize(dt)
            elif dt.tzinfo != self.utc_tz:
                dt = dt.astimezone(self.utc_tz)
            
            # Convert to local timezone
            local_dt = dt.astimezone(self.local_tz)
            
            logger.debug(f"UTC to local conversion: {dt} → {local_dt}")
            return local_dt
            
        except Exception as e:
            logger.error(f"UTC to local conversion failed: {e}")
            raise ValueError(f"Failed to convert UTC datetime: {utc_datetime}")
    
    def local_to_utc(self, local_datetime: Union[datetime, str, pd.Timestamp]) -> datetime:
        """
        Convert Pacific/Auckland datetime to UTC timezone
        
        Args:
            local_datetime: Local datetime (datetime, ISO string, or pandas Timestamp)
            
        Returns:
            UTC datetime
        """
        try:
            # Convert input to datetime if string
            if isinstance(local_datetime, str):
                dt = pd.to_datetime(local_datetime)
            elif isinstance(local_datetime, pd.Timestamp):
                dt = local_datetime.to_pydatetime()
            else:
                dt = local_datetime
            
            # Ensure datetime is local timezone aware
            if dt.tzinfo is None:
                dt = self.local_tz.localize(dt)
            elif dt.tzinfo != self.local_tz:
                dt = dt.astimezone(self.local_tz)
            
            # Convert to UTC
            utc_dt = dt.astimezone(self.utc_tz)
            
            logger.debug(f"Local to UTC conversion: {dt} → {utc_dt}")
            return utc_dt
            
        except Exception as e:
            logger.error(f"Local to UTC conversion failed: {e}")
            raise ValueError(f"Failed to convert local datetime: {local_datetime}")
    
    def process_dataframe_timestamps(
        self,
        df: pd.DataFrame,
        timestamp_column: str = 'timestamp',
        convert_to_local: bool = True
    ) -> pd.DataFrame:
        """
        Process timestamps in a DataFrame for timezone conversion
        
        Args:
            df: DataFrame with timestamp column
            timestamp_column: Name of timestamp column
            convert_to_local: If True, convert UTC to local; if False, convert local to UTC
            
        Returns:
            DataFrame with converted timestamps
        """
        try:
            if timestamp_column not in df.columns:
                logger.warning(f"Timestamp column '{timestamp_column}' not found in DataFrame")
                return df
            
            if df.empty:
                logger.debug("Empty DataFrame provided for timestamp processing")
                return df
            
            df_copy = df.copy()
            
            if convert_to_local:
                # Convert UTC timestamps to local timezone
                df_copy[timestamp_column] = pd.to_datetime(df_copy[timestamp_column], utc=True)
                df_copy[timestamp_column] = df_copy[timestamp_column].dt.tz_convert(self.local_tz)
                logger.debug(f"Converted {len(df_copy)} timestamps from UTC to local")
            else:
                # Convert local timestamps to UTC
                df_copy[timestamp_column] = pd.to_datetime(df_copy[timestamp_column])
                # If timezone naive, assume local timezone
                if df_copy[timestamp_column].dt.tz is None:
                    df_copy[timestamp_column] = df_copy[timestamp_column].dt.tz_localize(self.local_tz)
                df_copy[timestamp_column] = df_copy[timestamp_column].dt.tz_convert(self.utc_tz)
                logger.debug(f"Converted {len(df_copy)} timestamps from local to UTC")
            
            return df_copy
            
        except Exception as e:
            logger.error(f"DataFrame timestamp processing failed: {e}")
            raise ValueError(f"Failed to process DataFrame timestamps: {e}")
    
    def get_current_local_time(self) -> datetime:
        """
        Get current time in Pacific/Auckland timezone
        
        Returns:
            Current local datetime
        """
        return datetime.now(self.local_tz)
    
    def get_current_utc_time(self) -> datetime:
        """
        Get current time in UTC
        
        Returns:
            Current UTC datetime
        """
        return datetime.now(self.utc_tz)
    
    def validate_dst_transition(self, local_datetime: datetime) -> bool:
        """
        Validate if a local datetime falls during DST transition
        
        Args:
            local_datetime: Local datetime to check
            
        Returns:
            True if datetime is valid (not in DST gap), False otherwise
        """
        try:
            # Try to localize the datetime - this will raise an exception
            # if it falls in the DST gap
            if local_datetime.tzinfo is None:
                self.local_tz.localize(local_datetime)
            return True
        except pytz.exceptions.AmbiguousTimeError:
            logger.warning(f"Ambiguous time during DST transition: {local_datetime}")
            return False
        except pytz.exceptions.NonExistentTimeError:
            logger.warning(f"Non-existent time during DST transition: {local_datetime}")
            return False
        except Exception as e:
            logger.error(f"DST validation error: {e}")
            return False
    
    def get_timezone_info(self) -> dict:
        """
        Get timezone information and current DST status
        
        Returns:
            Dictionary with timezone information
        """
        current_utc = self.get_current_utc_time()
        current_local = self.get_current_local_time()
        
        # Check if currently in DST
        is_dst = current_local.dst().total_seconds() > 0
        
        return {
            'local_timezone': str(self.local_tz),
            'utc_timezone': str(self.utc_tz),
            'current_utc': current_utc.isoformat(),
            'current_local': current_local.isoformat(),
            'is_dst': is_dst,
            'utc_offset': current_local.utcoffset().total_seconds() / 3600,
            'dst_offset': current_local.dst().total_seconds() / 3600
        } 