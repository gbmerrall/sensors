"""
Data Aggregation Engine

Implements smart aggregation algorithms for sensor data based on time ranges
with support for interpolation vs averaging as designed in the creative phase.
"""

import pandas as pd
from typing import Dict, Optional, Union
from datetime import datetime, timedelta
from src.utils.config import Config
from src.utils.logging_setup import get_data_logger
from src.data.timezone_processor import TimezoneProcessor

logger = get_data_logger()


class AggregationEngine:
    """
    Smart aggregation engine for sensor data
    
    Implements the aggregation layer from the Hybrid Cached Pipeline Architecture
    with dynamic aggregation strategy selection based on time range and data density.
    """
    
    def __init__(self):
        """Initialize aggregation engine with timezone processor"""
        self.timezone_processor = TimezoneProcessor()
        self.aggregation_methods = Config.AGGREGATION_METHODS
        
        # Aggregation strategy thresholds (time range → strategy)
        self.strategy_thresholds = {
            'raw': timedelta(hours=6),      # < 6 hours: raw data
            'interpolation': timedelta(days=3),     # 6h-3d: 15min interpolation
            'hourly': timedelta(weeks=2),          # 3d-2w: hourly averages
            'daily': timedelta(days=90),           # 2w-90d: daily averages
            'weekly': timedelta(days=365)          # >90d: weekly averages
        }
        
        logger.info("Aggregation engine initialized with smart strategy selection")
    
    def determine_aggregation_strategy(
        self,
        start_time: datetime,
        end_time: datetime,
        data_count: Optional[int] = None
    ) -> str:
        """
        Determine optimal aggregation strategy based on time range and data density
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            data_count: Optional count of data points
            
        Returns:
            Aggregation strategy ('raw', 'interpolation', 'hourly', 'daily', 'weekly')
        """
        try:
            time_range = end_time - start_time
            
            # Determine strategy based on time range
            if time_range <= self.strategy_thresholds['raw']:
                strategy = 'raw'
            elif time_range <= self.strategy_thresholds['interpolation']:
                strategy = 'interpolation'
            elif time_range <= self.strategy_thresholds['hourly']:
                strategy = 'hourly'
            elif time_range <= self.strategy_thresholds['daily']:
                strategy = 'daily'
            else:
                strategy = 'weekly'
            
            # Adjust strategy based on data density if provided
            if data_count is not None:
                data_density = data_count / time_range.total_seconds() * 3600  # points per hour
                
                # If very high density and long range, increase aggregation
                if data_density > 100 and time_range > timedelta(days=1):
                    if strategy == 'interpolation':
                        strategy = 'hourly'
                    elif strategy == 'hourly':
                        strategy = 'daily'
                
                # If very low density, decrease aggregation
                elif data_density < 1 and time_range < timedelta(days=7):
                    if strategy == 'daily':
                        strategy = 'hourly'
                    elif strategy == 'hourly':
                        strategy = 'interpolation'
            
            logger.debug(f"Selected aggregation strategy: {strategy} for range {time_range} with {data_count} points")
            return strategy
            
        except Exception as e:
            logger.error(f"Failed to determine aggregation strategy: {e}")
            return 'hourly'  # Safe default
    
    def aggregate_temperature_humidity_data(
        self,
        df: pd.DataFrame,
        strategy: str = 'auto',
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Aggregate temperature and humidity data using specified strategy
        
        Args:
            df: DataFrame with temperature/humidity data
            strategy: Aggregation strategy or 'auto' for automatic selection
            start_time: Start time for auto strategy determination
            end_time: End time for auto strategy determination
            
        Returns:
            Aggregated DataFrame
        """
        try:
            if df.empty:
                logger.debug("Empty DataFrame provided for aggregation")
                return df
            
            # Convert timestamp column to datetime if needed
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
            
            # Auto-determine strategy if needed
            if strategy == 'auto':
                if start_time is None or end_time is None:
                    start_time = df['timestamp'].min()
                    end_time = df['timestamp'].max()
                strategy = self.determine_aggregation_strategy(start_time, end_time, len(df))
            
            logger.debug(f"Aggregating {len(df)} temperature/humidity records using {strategy} strategy")
            
            # Apply aggregation based on strategy
            if strategy == 'raw':
                return df
            elif strategy == 'interpolation':
                return self._interpolate_data(df, '15min')
            elif strategy == 'hourly':
                return self._aggregate_by_time(df, '1h')
            elif strategy == 'daily':
                return self._aggregate_by_time(df, '1D')
            elif strategy == 'weekly':
                return self._aggregate_by_time(df, '1W')
            else:
                logger.warning(f"Unknown aggregation strategy: {strategy}, using hourly")
                return self._aggregate_by_time(df, '1h')
                
        except Exception as e:
            logger.error(f"Temperature/humidity aggregation failed: {e}")
            return df  # Return original data on error
    
    def aggregate_battery_data(
        self,
        df: pd.DataFrame,
        strategy: str = 'auto',
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Aggregate battery data using specified strategy
        
        Args:
            df: DataFrame with battery data
            strategy: Aggregation strategy or 'auto' for automatic selection
            start_time: Start time for auto strategy determination
            end_time: End time for auto strategy determination
            
        Returns:
            Aggregated DataFrame
        """
        try:
            if df.empty:
                logger.debug("Empty DataFrame provided for battery aggregation")
                return df
            
            # Convert timestamp column to datetime if needed
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
            
            # Auto-determine strategy if needed
            if strategy == 'auto':
                if start_time is None or end_time is None:
                    start_time = df['timestamp'].min()
                    end_time = df['timestamp'].max()
                strategy = self.determine_aggregation_strategy(start_time, end_time, len(df))
            
            logger.debug(f"Aggregating {len(df)} battery records using {strategy} strategy")
            
            # Apply aggregation based on strategy
            if strategy == 'raw':
                return df
            else:
                # For battery data, use averaging for all aggregation levels
                return self._aggregate_battery_by_time(df, self.aggregation_methods.get(strategy, '1h'))
                
        except Exception as e:
            logger.error(f"Battery aggregation failed: {e}")
            return df  # Return original data on error
    
    def _interpolate_data(self, df: pd.DataFrame, freq: str) -> pd.DataFrame:
        """
        Interpolate data to fill gaps at specified frequency
        
        Args:
            df: DataFrame with timestamp and sensor data
            freq: Interpolation frequency (e.g., '15min')
            
        Returns:
            Interpolated DataFrame
        """
        try:
            if 'timestamp' not in df.columns:
                return df
            
            # For sensor data that doesn't align with regular intervals,
            # we should resample to the frequency instead of reindexing
            df_indexed = df.set_index('timestamp')
            
            # Group by location if present
            if 'location' in df.columns:
                # Define aggregation functions for resampling
                agg_funcs = {
                    'temperature': 'mean',
                    'humidity': 'mean'
                }
                if 'mac' in df.columns:
                    agg_funcs['mac'] = 'first'
                
                # Resample by location
                result = df_indexed.groupby('location').resample(freq).agg(agg_funcs).reset_index()
                
                # Interpolate missing values within each location group
                for location in result['location'].unique():
                    location_mask = result['location'] == location
                    numeric_columns = result.select_dtypes(include=['number']).columns
                    result.loc[location_mask, numeric_columns] = result.loc[location_mask, numeric_columns].interpolate(method='linear')
            else:
                # Simple case without location grouping
                result = df_indexed.resample(freq).mean().reset_index()
                
                # Interpolate missing values
                numeric_columns = result.select_dtypes(include=['number']).columns
                result[numeric_columns] = result[numeric_columns].interpolate(method='linear')
            
            # Remove any remaining NaN values
            result = result.dropna(subset=['temperature', 'humidity'])
            
            logger.debug(f"Interpolated data from {len(df)} to {len(result)} points at {freq} frequency")
            return result
            
        except Exception as e:
            logger.error(f"Data interpolation failed: {e}")
            return df
    
    def _aggregate_by_time(self, df: pd.DataFrame, freq: str) -> pd.DataFrame:
        """
        Aggregate temperature/humidity data by time periods using averages
        
        Args:
            df: DataFrame with timestamp and sensor data
            freq: Aggregation frequency (e.g., '1h', '1D')
            
        Returns:
            Aggregated DataFrame
        """
        try:
            if 'timestamp' not in df.columns:
                return df
            
            # Set timestamp as index for resampling
            df_indexed = df.set_index('timestamp')
            
            # Define aggregation functions based on available columns
            agg_funcs = {
                'temperature': 'mean',
                'humidity': 'mean'
            }
            if 'mac' in df.columns:
                agg_funcs['mac'] = 'first'  # Keep first MAC address for each group
            
            # Group by location if present and aggregate
            if 'location' in df.columns:
                result = df_indexed.groupby('location').resample(freq).agg(agg_funcs).reset_index()
            else:
                result = df_indexed.resample(freq).agg(agg_funcs).reset_index()
            
            # Remove NaN values
            result = result.dropna(subset=['temperature', 'humidity'])
            
            logger.debug(f"Aggregated data from {len(df)} to {len(result)} points at {freq} frequency")
            return result
            
        except Exception as e:
            logger.error(f"Time aggregation failed: {e}")
            return df
    
    def _aggregate_battery_by_time(self, df: pd.DataFrame, freq: str) -> pd.DataFrame:
        """
        Aggregate battery data by time periods
        
        Args:
            df: DataFrame with timestamp and battery data
            freq: Aggregation frequency (e.g., '1h', '1D')
            
        Returns:
            Aggregated DataFrame
        """
        try:
            if 'timestamp' not in df.columns:
                return df
            
            # Set timestamp as index for resampling
            df_indexed = df.set_index('timestamp')
            
            # Define aggregation functions based on available columns
            agg_funcs = {}
            if 'voltage' in df.columns:
                agg_funcs['voltage'] = 'mean'
            if 'percentage' in df.columns:
                agg_funcs['percentage'] = 'mean'
            if 'dischargerate' in df.columns:
                agg_funcs['dischargerate'] = 'mean'
            if 'mac' in df.columns:
                agg_funcs['mac'] = 'first'  # Keep first MAC address for each group
            
            # Group by location if present and aggregate
            if 'location' in df.columns:
                result = df_indexed.groupby('location').resample(freq).agg(agg_funcs).reset_index()
            else:
                result = df_indexed.resample(freq).agg(agg_funcs).reset_index()
            
            # Remove NaN values from available battery columns
            dropna_columns = []
            if 'voltage' in result.columns:
                dropna_columns.append('voltage')
            if 'percentage' in result.columns:
                dropna_columns.append('percentage')
            
            if dropna_columns:
                result = result.dropna(subset=dropna_columns)
            
            logger.debug(f"Aggregated battery data from {len(df)} to {len(result)} points at {freq} frequency")
            return result
            
        except Exception as e:
            logger.error(f"Battery time aggregation failed: {e}")
            return df
    
    def get_aggregation_summary(
        self,
        original_count: int,
        aggregated_count: int,
        strategy: str,
        time_range: timedelta
    ) -> Dict[str, Union[int, str, float]]:
        """
        Generate aggregation summary statistics
        
        Args:
            original_count: Original data point count
            aggregated_count: Aggregated data point count
            strategy: Aggregation strategy used
            time_range: Time range of data
            
        Returns:
            Dictionary with aggregation summary
        """
        return {
            'original_count': original_count,
            'aggregated_count': aggregated_count,
            'reduction_ratio': original_count / aggregated_count if aggregated_count > 0 else 0,
            'strategy': strategy,
            'time_range_hours': time_range.total_seconds() / 3600,
            'data_density_per_hour': aggregated_count / (time_range.total_seconds() / 3600) if time_range.total_seconds() > 0 else 0
        } 
