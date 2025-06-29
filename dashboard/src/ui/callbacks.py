"""
Dashboard Callback Functions

Implements callback functions to connect data processing with chart visualization
and handle user interactions as designed in the data flow architecture.
"""

import dash
from dash import Input, Output
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any

from src.data.database_manager import DatabaseConnectionManager
from src.data.timezone_processor import TimezoneProcessor
from src.data.aggregation_engine import AggregationEngine
from src.data.statistics_calculator import StatisticsCalculator
from src.ui.charts import ChartComponents
from src.utils.logging_setup import get_ui_logger

logger = get_ui_logger()


class DashboardCallbacks:
    """
    Dashboard callback functions manager
    
    Handles all dashboard interactivity including data loading,
    chart updates, and user interface responses.
    """
    
    def __init__(self, app: dash.Dash):
        """
        Initialize callback functions
        
        Args:
            app: Dash application instance
        """
        self.app = app
        self.db_manager = DatabaseConnectionManager()
        self.timezone_processor = TimezoneProcessor()
        self.aggregation_engine = AggregationEngine()
        self.statistics_calculator = StatisticsCalculator()
        self.chart_components = ChartComponents()
        
        # Register all callbacks
        self._register_callbacks()
        
        logger.info("Dashboard callbacks initialized and registered")
    
    def _register_callbacks(self):
        """Register all callback functions with the Dash app"""
        
        # Initialize data on app load
        self._register_initialization_callbacks()
        
        # Chart update callbacks
        self._register_chart_callbacks()
        
        # Statistics update callbacks
        self._register_statistics_callbacks()
        
        # Control panel callbacks
        self._register_control_callbacks()
        
        logger.debug("All callback functions registered")
    
    def _register_initialization_callbacks(self):
        """Register callbacks for app initialization"""
        
        @self.app.callback(
            [
                Output('location-dropdown', 'options'),
                Output('location-dropdown', 'value'),
                Output('date-range-picker', 'start_date'),
                Output('date-range-picker', 'end_date'),
                Output('sensor-data-store', 'data')
            ],
            [Input('auto-refresh-interval', 'n_intervals')]
        )
        def initialize_dashboard(n_intervals):
            """Initialize dashboard with default data and settings"""
            try:
                # Get available locations
                locations = self.db_manager.get_available_locations()
                location_options = [{'label': loc, 'value': loc} for loc in locations]
                
                # Set default date range to current day in Pacific/Auckland timezone
                if self.timezone_processor:
                    # Get current date in Pacific/Auckland timezone
                    utc_now = datetime.now(self.timezone_processor.utc_tz)
                    local_now = utc_now.astimezone(self.timezone_processor.local_tz)
                    current_date = local_now.date()
                    
                    # Set both start and end to current day
                    start_date = current_date
                    end_date = current_date
                    
                    # Convert to UTC for database query (database timestamps are in UTC)
                    start_local = self.timezone_processor.local_tz.localize(
                        datetime.combine(current_date, datetime.min.time())  # 00:00:00
                    )
                    end_local = self.timezone_processor.local_tz.localize(
                        datetime.combine(current_date, datetime.max.time().replace(microsecond=0))  # 23:59:59
                    )
                    
                    start_utc = start_local.astimezone(self.timezone_processor.utc_tz)
                    end_utc = end_local.astimezone(self.timezone_processor.utc_tz)
                    
                    initial_data = self._load_sensor_data(
                        start_utc.strftime('%Y-%m-%d %H:%M:%S'),
                        end_utc.strftime('%Y-%m-%d %H:%M:%S'),
                        locations
                    )
                    
                    logger.info(f"Dashboard initialized with current day: {current_date} (Pacific/Auckland)")
                    logger.debug(f"Database query range: {start_utc.strftime('%Y-%m-%d %H:%M:%S')} to {end_utc.strftime('%Y-%m-%d %H:%M:%S')} (UTC)")
                else:
                    # Fallback to system current date if no timezone processor
                    current_date = datetime.now().date()
                    start_date = current_date
                    end_date = current_date
                    
                    initial_data = self._load_sensor_data(
                        f"{current_date.strftime('%Y-%m-%d')} 00:00:00",
                        f"{current_date.strftime('%Y-%m-%d')} 23:59:59",
                        locations
                    )
                    
                    logger.warning("Timezone processor not available, using system date")
                
                return (
                    location_options,
                    locations,  # Select all locations by default
                    start_date,
                    end_date,
                    initial_data
                )
                
            except Exception as e:
                logger.error(f"Dashboard initialization failed: {e}")
                # Fallback to system current date
                current_date = datetime.now().date()
                return [], [], current_date, current_date, {}
    
    def _register_chart_callbacks(self):
        """Register callbacks for chart updates"""
        
        @self.app.callback(
            [
                Output('temperature-chart', 'figure'),
                Output('humidity-chart', 'figure'),
                Output('battery-chart', 'figure')
            ],
            [
                Input('sensor-data-store', 'data'),
                Input('aggregation-dropdown', 'value')
            ]
        )
        def update_charts(sensor_data, aggregation_method):
            """Update all charts based on current data and settings"""
            try:
                if not sensor_data:
                    empty_fig = self.chart_components._create_empty_chart("No data available")
                    return empty_fig, empty_fig, empty_fig
                
                # Extract data from store
                temp_humidity_data = sensor_data.get('temperature_humidity', [])
                battery_data = sensor_data.get('battery', [])
                
                # Convert to DataFrames
                temp_humidity_df = pd.DataFrame(temp_humidity_data) if temp_humidity_data else pd.DataFrame()
                battery_df = pd.DataFrame(battery_data) if battery_data else pd.DataFrame()
                
                # Apply aggregation if requested
                if aggregation_method and aggregation_method != 'raw':
                    if not temp_humidity_df.empty:
                        temp_humidity_df = self.aggregation_engine.aggregate_temperature_humidity_data(
                            temp_humidity_df, strategy=aggregation_method
                        )
                    
                    if not battery_df.empty:
                        battery_df = self.aggregation_engine.aggregate_battery_data(
                            battery_df, strategy=aggregation_method
                        )
                
                # Create charts
                temp_chart = self.chart_components.create_temperature_chart(temp_humidity_df)
                humidity_chart = self.chart_components.create_humidity_chart(temp_humidity_df)
                battery_chart = self.chart_components.create_battery_chart(battery_df)
                
                logger.debug("Charts updated successfully")
                return temp_chart, humidity_chart, battery_chart
                
            except Exception as e:
                logger.error(f"Chart update failed: {e}")
                empty_fig = self.chart_components._create_empty_chart("Error updating charts")
                return empty_fig, empty_fig, empty_fig
    
    def _register_statistics_callbacks(self):
        """Register callbacks for statistics updates"""
        
        @self.app.callback(
            [
                Output('temp-avg', 'children'),
                Output('temp-range', 'children'),
                Output('humidity-avg', 'children'),
                Output('humidity-range', 'children'),
                Output('battery-avg', 'children'),
                Output('battery-range', 'children'),
                Output('data-points', 'children'),
                Output('last-updated', 'children')
            ],
            [Input('sensor-data-store', 'data')]
        )
        def update_statistics(sensor_data):
            """Update statistics cards based on current data"""
            try:
                if not sensor_data:
                    return "--°C", "Min: --°C | Max: --°C", "--%", "Min: --% | Max: --%", \
                           "--V", "Min: --V | Max: --V", "--", "Last updated: --"
                
                # Extract data
                temp_humidity_data = sensor_data.get('temperature_humidity', [])
                battery_data = sensor_data.get('battery', [])
                
                # Convert to DataFrames
                temp_humidity_df = pd.DataFrame(temp_humidity_data) if temp_humidity_data else pd.DataFrame()
                battery_df = pd.DataFrame(battery_data) if battery_data else pd.DataFrame()
                
                # Calculate temperature statistics
                temp_avg = "--°C"
                temp_range = "Min: --°C | Max: --°C"
                if not temp_humidity_df.empty and 'temperature' in temp_humidity_df.columns:
                    temp_stats = self.statistics_calculator.calculate_basic_statistics(
                        temp_humidity_df, ['temperature']
                    )
                    if 'temperature' in temp_stats and 'overall' in temp_stats['temperature']:
                        stats = temp_stats['temperature']['overall']
                        temp_avg = f"{stats['mean']:.1f}°C"
                        temp_range = f"Min: {stats['min']:.1f}°C | Max: {stats['max']:.1f}°C"
                
                # Calculate humidity statistics
                humidity_avg = "--%"
                humidity_range = "Min: --% | Max: --%"
                if not temp_humidity_df.empty and 'humidity' in temp_humidity_df.columns:
                    humidity_stats = self.statistics_calculator.calculate_basic_statistics(
                        temp_humidity_df, ['humidity']
                    )
                    if 'humidity' in humidity_stats and 'overall' in humidity_stats['humidity']:
                        stats = humidity_stats['humidity']['overall']
                        humidity_avg = f"{stats['mean']:.1f}%"
                        humidity_range = f"Min: {stats['min']:.1f}% | Max: {stats['max']:.1f}%"
                
                # Calculate battery statistics - prioritize voltage
                battery_avg = "--V"
                battery_range = "Min: --V | Max: --V"
                battery_column = None
                
                if not battery_df.empty:
                    # Find available battery column - prioritize voltage
                    for col in ['voltage', 'percentage']:
                        if col in battery_df.columns:
                            battery_column = col
                            break
                    
                    if battery_column:
                        battery_stats = self.statistics_calculator.calculate_basic_statistics(
                            battery_df, [battery_column]
                        )
                        if battery_column in battery_stats and 'overall' in battery_stats[battery_column]:
                            stats = battery_stats[battery_column]['overall']
                            unit = "V" if battery_column == 'voltage' else "%"
                            precision = 2 if battery_column == 'voltage' else 1  # Higher precision for voltage
                            battery_avg = f"{stats['mean']:.{precision}f}{unit}"
                            battery_range = f"Min: {stats['min']:.{precision}f}{unit} | Max: {stats['max']:.{precision}f}{unit}"
                
                # Calculate data points and last updated
                total_points = len(temp_humidity_data) + len(battery_data)
                last_updated = datetime.now().strftime("%H:%M:%S")
                
                logger.debug(f"Statistics updated - {total_points} data points")
                
                return (
                    temp_avg, temp_range,
                    humidity_avg, humidity_range,
                    battery_avg, battery_range,
                    str(total_points), f"Last updated: {last_updated}"
                )
                
            except Exception as e:
                logger.error(f"Statistics update failed: {e}")
                return "--°C", "Min: --°C | Max: --°C", "--%", "Min: --% | Max: --%", \
                       "--V", "Min: --V | Max: --V", "--", "Last updated: Error"
    
    def _register_control_callbacks(self):
        """Register callbacks for control panel interactions"""
        
        @self.app.callback(
            Output('sensor-data-store', 'data', allow_duplicate=True),
            [
                Input('refresh-button', 'n_clicks'),
                Input('date-range-picker', 'start_date'),
                Input('date-range-picker', 'end_date'),
                Input('location-dropdown', 'value')
            ],
            prevent_initial_call=True
        )
        def refresh_data(n_clicks, start_date, end_date, selected_locations):
            """Refresh sensor data based on selected filters"""
            try:
                if not start_date or not end_date:
                    logger.warning("Invalid date range for data refresh")
                    return {}
                
                # Convert dates to datetime with proper time boundaries in local timezone
                # Then convert to UTC for database query (database timestamps are in UTC)
                if self.timezone_processor:
                    # Create local timezone datetime objects
                    start_local = self.timezone_processor.local_tz.localize(
                        pd.to_datetime(start_date).replace(hour=0, minute=0, second=0)
                    )
                    end_local = self.timezone_processor.local_tz.localize(
                        pd.to_datetime(end_date).replace(hour=23, minute=59, second=59)
                    )
                    
                    # Convert to UTC for database query
                    start_utc = start_local.astimezone(self.timezone_processor.utc_tz)
                    end_utc = end_local.astimezone(self.timezone_processor.utc_tz)
                    
                    start_datetime = start_utc.strftime('%Y-%m-%d %H:%M:%S')
                    end_datetime = end_utc.strftime('%Y-%m-%d %H:%M:%S')
                    
                    logger.debug(f"Date range conversion: {start_date} to {end_date} (local) → {start_datetime} to {end_datetime} (UTC)")
                else:
                    # Fallback to original method if no timezone processor
                    start_datetime = pd.to_datetime(start_date).strftime('%Y-%m-%d 00:00:00')
                    end_datetime = pd.to_datetime(end_date).strftime('%Y-%m-%d 23:59:59')
                
                # Use selected locations or all available locations
                locations = selected_locations if selected_locations else self.db_manager.get_available_locations()
                
                # Load data
                data = self._load_sensor_data(start_datetime, end_datetime, locations)
                
                logger.info(f"Data refreshed for {len(locations)} locations from {start_date} to {end_date}")
                return data
                
            except Exception as e:
                logger.error(f"Data refresh failed: {e}")
                return {}
    
    def _load_sensor_data(
        self,
        start_time: str,
        end_time: str,
        locations: List[str]
    ) -> Dict[str, Any]:
        """
        Load sensor data from database
        
        Args:
            start_time: Start timestamp (ISO format)
            end_time: End timestamp (ISO format)
            locations: List of location names
            
        Returns:
            Dictionary with temperature/humidity and battery data
        """
        try:
            data = {}
            
            # Load temperature/humidity data
            temp_humidity_df = self.db_manager.get_temperature_humidity_data(
                start_time, end_time, locations
            )
            
            if temp_humidity_df is not None and not temp_humidity_df.empty:
                # Convert timestamps to local timezone if timezone processor is available
                if self.timezone_processor:
                    temp_humidity_df = self.timezone_processor.process_dataframe_timestamps(
                        temp_humidity_df, convert_to_local=True
                    )
                data['temperature_humidity'] = temp_humidity_df.to_dict('records')
            else:
                data['temperature_humidity'] = []
            
            # Load battery data
            battery_df = self.db_manager.get_battery_data(
                start_time, end_time, locations
            )
            
            if battery_df is not None and not battery_df.empty:
                # Convert timestamps to local timezone if timezone processor is available
                if self.timezone_processor:
                    battery_df = self.timezone_processor.process_dataframe_timestamps(
                        battery_df, convert_to_local=True
                    )
                data['battery'] = battery_df.to_dict('records')
            else:
                data['battery'] = []
            
            logger.debug(f"Loaded {len(data.get('temperature_humidity', []))} temp/humidity records and {len(data.get('battery', []))} battery records")
            return data
            
        except Exception as e:
            logger.error(f"Failed to load sensor data: {e}")
            return {'temperature_humidity': [], 'battery': []}
    
    def get_callback_info(self) -> Dict[str, Any]:
        """Get information about registered callbacks"""
        return {
            'callback_types': [
                'Initialization callbacks',
                'Chart update callbacks', 
                'Statistics callbacks',
                'Control panel callbacks'
            ],
            'data_flow': [
                'Database → Processing → Visualization',
                'User input → Data refresh → Chart update',
                'Aggregation selection → Chart re-render',
                'Statistics calculation → Display update'
            ],
            'interactive_elements': [
                'Date range picker',
                'Location dropdown',
                'Aggregation selector',
                'Refresh button'
            ]
        } 