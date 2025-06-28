"""
Statistics Calculator

Provides statistical analysis and calculation functions for sensor data
including min, max, average, trends, and multi-location comparisons.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from src.utils.logging_setup import get_data_logger

logger = get_data_logger()


class StatisticsCalculator:
    """
    Statistics calculator for sensor data analysis
    
    Provides comprehensive statistical analysis including basic statistics,
    trends, correlations, and multi-location comparisons.
    """
    
    def __init__(self):
        """Initialize statistics calculator"""
        logger.info("Statistics calculator initialized")
    
    def calculate_basic_statistics(
        self,
        df: pd.DataFrame,
        value_columns: List[str],
        group_by: Optional[str] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate basic statistics (min, max, mean, std) for specified columns
        
        Args:
            df: DataFrame with sensor data
            value_columns: List of columns to analyze
            group_by: Optional column to group by (e.g., 'location')
            
        Returns:
            Dictionary with statistics for each column
        """
        try:
            if df.empty:
                logger.debug("Empty DataFrame provided for basic statistics")
                return {}
            
            stats = {}
            
            if group_by and group_by in df.columns:
                # Calculate statistics by group
                for column in value_columns:
                    if column in df.columns:
                        column_stats = {}
                        grouped = df.groupby(group_by)[column]
                        
                        for group_name, group_data in grouped:
                            column_stats[str(group_name)] = {
                                'count': int(group_data.count()),
                                'min': float(group_data.min()) if not group_data.empty else 0.0,
                                'max': float(group_data.max()) if not group_data.empty else 0.0,
                                'mean': float(group_data.mean()) if not group_data.empty else 0.0,
                                'std': float(group_data.std()) if not group_data.empty else 0.0,
                                'median': float(group_data.median()) if not group_data.empty else 0.0,
                                'q25': float(group_data.quantile(0.25)) if not group_data.empty else 0.0,
                                'q75': float(group_data.quantile(0.75)) if not group_data.empty else 0.0
                            }
                        
                        stats[column] = column_stats
            else:
                # Calculate overall statistics
                for column in value_columns:
                    if column in df.columns:
                        series = df[column].dropna()
                        stats[column] = {
                            'overall': {
                                'count': int(series.count()),
                                'min': float(series.min()) if not series.empty else 0.0,
                                'max': float(series.max()) if not series.empty else 0.0,
                                'mean': float(series.mean()) if not series.empty else 0.0,
                                'std': float(series.std()) if not series.empty else 0.0,
                                'median': float(series.median()) if not series.empty else 0.0,
                                'q25': float(series.quantile(0.25)) if not series.empty else 0.0,
                                'q75': float(series.quantile(0.75)) if not series.empty else 0.0
                            }
                        }
            
            logger.debug(f"Calculated basic statistics for {len(value_columns)} columns")
            return stats
            
        except Exception as e:
            logger.error(f"Basic statistics calculation failed: {e}")
            return {}
    
    def calculate_temperature_humidity_stats(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Calculate temperature and humidity specific statistics
        
        Args:
            df: DataFrame with temperature and humidity data
            
        Returns:
            Dictionary with temperature and humidity statistics
        """
        try:
            if df.empty or 'temperature' not in df.columns or 'humidity' not in df.columns:
                logger.debug("Invalid DataFrame for temperature/humidity statistics")
                return {}
            
            stats = {}
            
            # Basic statistics for temperature and humidity
            basic_stats = self.calculate_basic_statistics(
                df, 
                ['temperature', 'humidity'], 
                'location' if 'location' in df.columns else None
            )
            stats.update(basic_stats)
            
            # Calculate comfort index (simple comfort metric)
            if 'location' in df.columns:
                for location in df['location'].unique():
                    location_data = df[df['location'] == location]
                    comfort_stats = self._calculate_comfort_index(location_data)
                    
                    # Add comfort stats to existing location stats
                    if 'temperature' in stats:
                        if str(location) in stats['temperature']:
                            stats['temperature'][str(location)].update(comfort_stats)
            else:
                comfort_stats = self._calculate_comfort_index(df)
                if 'temperature' in stats and 'overall' in stats['temperature']:
                    stats['temperature']['overall'].update(comfort_stats)
            
            logger.debug("Calculated temperature/humidity statistics with comfort index")
            return stats
            
        except Exception as e:
            logger.error(f"Temperature/humidity statistics calculation failed: {e}")
            return {}
    
    def calculate_battery_stats(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Calculate battery specific statistics including health indicators
        
        Args:
            df: DataFrame with battery data
            
        Returns:
            Dictionary with battery statistics
        """
        try:
            if df.empty:
                logger.debug("Empty DataFrame for battery statistics")
                return {}
            
            # Determine available battery columns
            battery_columns = []
            for col in ['voltage', 'percentage', 'dischargerate']:
                if col in df.columns:
                    battery_columns.append(col)
            
            if not battery_columns:
                logger.debug("No battery columns found for statistics")
                return {}
            
            stats = {}
            
            # Basic statistics for battery metrics
            basic_stats = self.calculate_basic_statistics(
                df, 
                battery_columns, 
                'location' if 'location' in df.columns else None
            )
            stats.update(basic_stats)
            
            # Calculate battery health indicators
            if 'percentage' in df.columns:
                health_stats = self._calculate_battery_health(df)
                
                if 'location' in df.columns:
                    for location in df['location'].unique():
                        location_data = df[df['location'] == location]
                        location_health = self._calculate_battery_health(location_data)
                        
                        # Add health stats to existing location stats
                        if 'percentage' in stats and str(location) in stats['percentage']:
                            stats['percentage'][str(location)].update(location_health)
                else:
                    if 'percentage' in stats and 'overall' in stats['percentage']:
                        stats['percentage']['overall'].update(health_stats)
            
            logger.debug("Calculated battery statistics with health indicators")
            return stats
            
        except Exception as e:
            logger.error(f"Battery statistics calculation failed: {e}")
            return {}
    
    def calculate_trends(
        self,
        df: pd.DataFrame,
        value_column: str,
        time_column: str = 'timestamp',
        group_by: Optional[str] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate trend analysis for time series data
        
        Args:
            df: DataFrame with time series data
            value_column: Column to analyze for trends
            time_column: Timestamp column name
            group_by: Optional column to group by
            
        Returns:
            Dictionary with trend analysis
        """
        try:
            if df.empty or value_column not in df.columns or time_column not in df.columns:
                logger.debug("Invalid DataFrame for trend analysis")
                return {}
            
            trends = {}
            
            # Ensure timestamp is datetime
            df[time_column] = pd.to_datetime(df[time_column])
            df = df.sort_values(time_column)
            
            if group_by and group_by in df.columns:
                # Calculate trends by group
                for group_name, group_data in df.groupby(group_by):
                    if len(group_data) >= 2:  # Need at least 2 points for trend
                        trend_stats = self._calculate_trend_stats(group_data, value_column, time_column)
                        trends[str(group_name)] = trend_stats
            else:
                # Calculate overall trend
                if len(df) >= 2:
                    trend_stats = self._calculate_trend_stats(df, value_column, time_column)
                    trends['overall'] = trend_stats
            
            logger.debug(f"Calculated trends for {value_column}")
            return trends
            
        except Exception as e:
            logger.error(f"Trend calculation failed: {e}")
            return {}
    
    def _calculate_comfort_index(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate comfort index based on temperature and humidity
        
        Args:
            df: DataFrame with temperature and humidity data
            
        Returns:
            Dictionary with comfort metrics
        """
        try:
            if df.empty or 'temperature' not in df.columns or 'humidity' not in df.columns:
                return {}
            
            temp_data = df['temperature'].dropna()
            humidity_data = df['humidity'].dropna()
            
            # Comfort ranges (these are example ranges - adjust based on requirements)
            temp_comfort_min, temp_comfort_max = 18.0, 26.0  # Celsius
            humidity_comfort_min, humidity_comfort_max = 30.0, 70.0  # Percentage
            
            # Calculate percentage of readings within comfort ranges
            temp_comfort_count = len(temp_data[(temp_data >= temp_comfort_min) & (temp_data <= temp_comfort_max)])
            humidity_comfort_count = len(humidity_data[(humidity_data >= humidity_comfort_min) & (humidity_data <= humidity_comfort_max)])
            
            comfort_stats = {
                'temp_comfort_percentage': (temp_comfort_count / len(temp_data) * 100) if len(temp_data) > 0 else 0.0,
                'humidity_comfort_percentage': (humidity_comfort_count / len(humidity_data) * 100) if len(humidity_data) > 0 else 0.0,
                'temp_comfort_range_min': temp_comfort_min,
                'temp_comfort_range_max': temp_comfort_max,
                'humidity_comfort_range_min': humidity_comfort_min,
                'humidity_comfort_range_max': humidity_comfort_max
            }
            
            # Overall comfort score (average of temp and humidity comfort)
            comfort_stats['overall_comfort_score'] = (
                comfort_stats['temp_comfort_percentage'] + 
                comfort_stats['humidity_comfort_percentage']
            ) / 2
            
            return comfort_stats
            
        except Exception as e:
            logger.error(f"Comfort index calculation failed: {e}")
            return {}
    
    def _calculate_battery_health(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate battery health indicators
        
        Args:
            df: DataFrame with battery data
            
        Returns:
            Dictionary with battery health metrics
        """
        try:
            if df.empty or 'percentage' not in df.columns:
                return {}
            
            percentage_data = df['percentage'].dropna()
            
            if percentage_data.empty:
                return {}
            
            # Health thresholds
            critical_threshold = 20.0  # Below 20% is critical
            low_threshold = 40.0       # Below 40% is low
            good_threshold = 70.0      # Above 70% is good
            
            # Calculate health distribution
            critical_count = len(percentage_data[percentage_data < critical_threshold])
            low_count = len(percentage_data[(percentage_data >= critical_threshold) & (percentage_data < low_threshold)])
            medium_count = len(percentage_data[(percentage_data >= low_threshold) & (percentage_data < good_threshold)])
            good_count = len(percentage_data[percentage_data >= good_threshold])
            
            total_readings = len(percentage_data)
            
            health_stats = {
                'critical_percentage': (critical_count / total_readings * 100) if total_readings > 0 else 0.0,
                'low_percentage': (low_count / total_readings * 100) if total_readings > 0 else 0.0,
                'medium_percentage': (medium_count / total_readings * 100) if total_readings > 0 else 0.0,
                'good_percentage': (good_count / total_readings * 100) if total_readings > 0 else 0.0,
                'average_battery_level': float(percentage_data.mean()),
                'lowest_battery_level': float(percentage_data.min()),
                'battery_health_score': max(0, min(100, float(percentage_data.mean())))  # Normalized 0-100
            }
            
            return health_stats
            
        except Exception as e:
            logger.error(f"Battery health calculation failed: {e}")
            return {}
    
    def _calculate_trend_stats(
        self,
        df: pd.DataFrame,
        value_column: str,
        time_column: str
    ) -> Dict[str, float]:
        """
        Calculate trend statistics for a time series
        
        Args:
            df: DataFrame with time series data
            value_column: Column to analyze
            time_column: Timestamp column
            
        Returns:
            Dictionary with trend statistics
        """
        try:
            if len(df) < 2:
                return {}
            
            # Convert timestamps to numeric for regression
            df_sorted = df.sort_values(time_column)
            time_numeric = pd.to_numeric(df_sorted[time_column])
            values = df_sorted[value_column].dropna()
            
            if len(values) < 2:
                return {}
            
            # Simple linear regression (slope calculation)
            time_aligned = time_numeric.iloc[:len(values)].reset_index(drop=True)
            values_aligned = values.reset_index(drop=True)
            
            # Calculate slope using numpy polyfit
            if len(time_aligned) >= 2:
                slope, intercept = np.polyfit(time_aligned, values_aligned, 1)
                
                # Calculate correlation coefficient
                correlation = np.corrcoef(time_aligned, values_aligned)[0, 1] if len(time_aligned) > 1 else 0.0
                
                # Determine trend direction
                if abs(slope) < 1e-10:  # Very small slope
                    trend_direction = "stable"
                elif slope > 0:
                    trend_direction = "increasing"
                else:
                    trend_direction = "decreasing"
                
                # Calculate trend strength based on correlation
                if abs(correlation) > 0.7:
                    trend_strength = "strong"
                elif abs(correlation) > 0.4:
                    trend_strength = "moderate"
                else:
                    trend_strength = "weak"
                
                return {
                    'slope': float(slope),
                    'correlation': float(correlation),
                    'trend_direction': trend_direction,
                    'trend_strength': trend_strength,
                    'data_points': len(values),
                    'time_span_hours': (time_aligned.max() - time_aligned.min()) / (1e9 * 3600)  # Convert nanoseconds to hours
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Trend statistics calculation failed: {e}")
            return {} 