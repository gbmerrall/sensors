"""
Chart Components

Implements chart visualization components for temperature, humidity, and battery data
with multi-location support as designed in the chart visualization creative phase.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Any
from datetime import datetime
from src.utils.config import Config
from src.utils.logging_setup import get_ui_logger

logger = get_ui_logger()


class ChartComponents:
    """
    Chart components for sensor data visualization
    
    Implements separate charts per data type as designed in the creative phase
    with multi-location support and interactive features.
    """
    
    def __init__(self):
        """Initialize chart components with styling configuration"""
        self.chart_config = Config.CHART_CONFIG
        
        # Color palette for multi-location visualization
        self.color_palette = [
            '#e74c3c',  # Red
            '#3498db',  # Blue
            '#2ecc71',  # Green
            '#f39c12',  # Orange
            '#9b59b6',  # Purple
            '#1abc9c',  # Turquoise
            '#34495e',  # Dark grey
            '#e67e22'   # Dark orange
        ]
        
        # Chart styling
        self.chart_style = {
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'font': {'family': 'Inter, sans-serif', 'size': 12},
            'showlegend': True,
            'legend': {'x': 0, 'y': 1.1, 'orientation': 'h'},
            'margin': {'l': 40, 'r': 40, 't': 40, 'b': 40}
        }
        
        logger.info("Chart components initialized with styling configuration")
    
    def create_temperature_chart(
        self,
        df: pd.DataFrame,
        title: str = "Temperature Over Time"
    ) -> go.Figure:
        """
        Create temperature chart with multi-location support
        
        Args:
            df: DataFrame with temperature data
            title: Chart title
            
        Returns:
            Plotly figure object
        """
        try:
            if df.empty or 'timestamp' not in df.columns or 'temperature' not in df.columns:
                logger.warning("Invalid DataFrame for temperature chart")
                return self._create_empty_chart("No temperature data available")
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            fig = go.Figure()
            
            # Check if multi-location data
            if 'location' in df.columns and df['location'].nunique() > 1:
                # Multi-location chart
                locations = df['location'].unique()
                for i, location in enumerate(locations):
                    location_data = df[df['location'] == location]
                    
                    fig.add_trace(go.Scatter(
                        x=location_data['timestamp'],
                        y=location_data['temperature'],
                        mode='lines+markers',
                        name=f'{location}',
                        line=dict(
                            color=self.color_palette[i % len(self.color_palette)],
                            width=2
                        ),
                        marker=dict(size=4),
                        hovertemplate=(
                            f'<b>{location}</b><br>'
                            'Time: %{x}<br>'
                            'Temperature: %{y:.1f}°C<br>'
                            '<extra></extra>'
                        )
                    ))
            else:
                # Single location chart
                location = df['location'].iloc[0] if 'location' in df.columns else 'Unknown'
                
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df['temperature'],
                    mode='lines+markers',
                    name=f'Temperature - {location}',
                    line=dict(color='#e74c3c', width=2),
                    marker=dict(size=4),
                    hovertemplate=(
                        '<b>Temperature</b><br>'
                        'Time: %{x}<br>'
                        'Temperature: %{y:.1f}°C<br>'
                        '<extra></extra>'
                    )
                ))
            
            # Update layout
            fig.update_layout(
                title=dict(text=title, x=0.5, font=dict(size=16, weight='bold')),
                xaxis_title="Time",
                yaxis_title="Temperature (°C)",
                yaxis=dict(range=[10, 30]),  # Fixed Y-axis range for temperature
                height=self.chart_config['default_height'],
                **self.chart_style
            )
            
            # Add grid
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
            
            # Add comfort zone if multiple data points
            if len(df) > 1:
                self._add_temperature_comfort_zone(fig, df['timestamp'].min(), df['timestamp'].max())
            
            logger.debug(f"Temperature chart created with {len(df)} data points")
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create temperature chart: {e}")
            return self._create_empty_chart("Error creating temperature chart")
    
    def create_humidity_chart(
        self,
        df: pd.DataFrame,
        title: str = "Humidity Over Time"
    ) -> go.Figure:
        """
        Create humidity chart with multi-location support
        
        Args:
            df: DataFrame with humidity data
            title: Chart title
            
        Returns:
            Plotly figure object
        """
        try:
            if df.empty or 'timestamp' not in df.columns or 'humidity' not in df.columns:
                logger.warning("Invalid DataFrame for humidity chart")
                return self._create_empty_chart("No humidity data available")
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            fig = go.Figure()
            
            # Check if multi-location data
            if 'location' in df.columns and df['location'].nunique() > 1:
                # Multi-location chart
                locations = df['location'].unique()
                for i, location in enumerate(locations):
                    location_data = df[df['location'] == location]
                    
                    fig.add_trace(go.Scatter(
                        x=location_data['timestamp'],
                        y=location_data['humidity'],
                        mode='lines+markers',
                        name=f'{location}',
                        line=dict(
                            color=self.color_palette[i % len(self.color_palette)],
                            width=2
                        ),
                        marker=dict(size=4),
                        hovertemplate=(
                            f'<b>{location}</b><br>'
                            'Time: %{x}<br>'
                            'Humidity: %{y:.1f}%<br>'
                            '<extra></extra>'
                        )
                    ))
            else:
                # Single location chart
                location = df['location'].iloc[0] if 'location' in df.columns else 'Unknown'
                
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df['humidity'],
                    mode='lines+markers',
                    name=f'Humidity - {location}',
                    line=dict(color='#3498db', width=2),
                    marker=dict(size=4),
                    hovertemplate=(
                        '<b>Humidity</b><br>'
                        'Time: %{x}<br>'
                        'Humidity: %{y:.1f}%<br>'
                        '<extra></extra>'
                    )
                ))
            
            # Update layout
            fig.update_layout(
                title=dict(text=title, x=0.5, font=dict(size=16, weight='bold')),
                xaxis_title="Time",
                yaxis_title="Humidity (%)",
                yaxis=dict(range=[30, 100]),  # Fixed Y-axis range for humidity
                height=self.chart_config['default_height'],
                **self.chart_style
            )
            
            # Add grid
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
            
            # Add comfort zone if multiple data points
            if len(df) > 1:
                self._add_humidity_comfort_zone(fig, df['timestamp'].min(), df['timestamp'].max())
            
            logger.debug(f"Humidity chart created with {len(df)} data points")
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create humidity chart: {e}")
            return self._create_empty_chart("Error creating humidity chart")
    
    def create_battery_chart(
        self,
        df: pd.DataFrame,
        title: str = "Battery Voltage Over Time"
    ) -> go.Figure:
        """
        Create battery chart with multi-location support, prioritizing voltage display
        
        Args:
            df: DataFrame with battery data
            title: Chart title
            
        Returns:
            Plotly figure object
        """
        try:
            if df.empty or 'timestamp' not in df.columns:
                logger.warning("Invalid DataFrame for battery chart")
                return self._create_empty_chart("No battery data available")
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            fig = go.Figure()
            
            # Determine which battery column to use - prioritize voltage
            battery_column = None
            for col in ['voltage', 'percentage']:
                if col in df.columns:
                    battery_column = col
                    break
            
            if battery_column is None:
                logger.warning("No battery percentage or voltage column found")
                return self._create_empty_chart("No battery data columns available")
            
            # Set up y-axis title and unit based on data type
            y_title = "Battery Voltage (V)" if battery_column == 'voltage' else "Battery Level (%)"
            unit = "V" if battery_column == 'voltage' else "%"
            
            # Check if multi-location data
            if 'location' in df.columns and df['location'].nunique() > 1:
                # Multi-location chart
                locations = df['location'].unique()
                for i, location in enumerate(locations):
                    location_data = df[df['location'] == location]
                    
                    fig.add_trace(go.Scatter(
                        x=location_data['timestamp'],
                        y=location_data[battery_column],
                        mode='lines+markers',
                        name=f'{location}',
                        line=dict(
                            color=self.color_palette[i % len(self.color_palette)],
                            width=2
                        ),
                        marker=dict(size=4),
                        hovertemplate=(
                            f'<b>{location}</b><br>'
                            'Time: %{x}<br>'
                            f'{battery_column.title()}: %{{y:.2f}}{unit}<br>'
                            '<extra></extra>'
                        )
                    ))
            else:
                # Single location chart
                location = df['location'].iloc[0] if 'location' in df.columns else 'Unknown'
                
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df[battery_column],
                    mode='lines+markers',
                    name=f'Battery - {location}',
                    line=dict(color='#2ecc71', width=2),
                    marker=dict(size=4),
                    hovertemplate=(
                        f'<b>Battery {battery_column.title()}</b><br>'
                        'Time: %{x}<br>'
                        f'{battery_column.title()}: %{{y:.2f}}{unit}<br>'
                        '<extra></extra>'
                    )
                ))
            
            # Update layout
            fig.update_layout(
                title=dict(text=title, x=0.5, font=dict(size=16, weight='bold')),
                xaxis_title="Time",
                yaxis_title=y_title,
                height=self.chart_config['default_height'],
                **self.chart_style
            )
            
            # Add grid
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
            
            # Add warning zones based on battery data type
            if len(df) > 1:
                if battery_column == 'percentage':
                    self._add_battery_warning_zones(fig, df['timestamp'].min(), df['timestamp'].max())
                elif battery_column == 'voltage':
                    self._add_battery_voltage_warning_zones(fig, df['timestamp'].min(), df['timestamp'].max())
            
            logger.debug(f"Battery chart created with {len(df)} data points")
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create battery chart: {e}")
            return self._create_empty_chart("Error creating battery chart")
    
    def create_combined_chart(
        self,
        temp_df: pd.DataFrame,
        humidity_df: pd.DataFrame,
        title: str = "Temperature & Humidity Overview"
    ) -> go.Figure:
        """
        Create combined temperature and humidity chart with dual y-axes
        
        Args:
            temp_df: DataFrame with temperature data
            humidity_df: DataFrame with humidity data
            title: Chart title
            
        Returns:
            Plotly figure object with dual y-axes
        """
        try:
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Temperature trace
            if not temp_df.empty and 'timestamp' in temp_df.columns and 'temperature' in temp_df.columns:
                temp_df['timestamp'] = pd.to_datetime(temp_df['timestamp'])
                temp_df = temp_df.sort_values('timestamp')
                
                fig.add_trace(
                    go.Scatter(
                        x=temp_df['timestamp'],
                        y=temp_df['temperature'],
                        mode='lines+markers',
                        name='Temperature',
                        line=dict(color='#e74c3c', width=2),
                        marker=dict(size=4),
                        hovertemplate=(
                            '<b>Temperature</b><br>'
                            'Time: %{x}<br>'
                            'Temperature: %{y:.1f}°C<br>'
                            '<extra></extra>'
                        )
                    ),
                    secondary_y=False
                )
            
            # Humidity trace
            if not humidity_df.empty and 'timestamp' in humidity_df.columns and 'humidity' in humidity_df.columns:
                humidity_df['timestamp'] = pd.to_datetime(humidity_df['timestamp'])
                humidity_df = humidity_df.sort_values('timestamp')
                
                fig.add_trace(
                    go.Scatter(
                        x=humidity_df['timestamp'],
                        y=humidity_df['humidity'],
                        mode='lines+markers',
                        name='Humidity',
                        line=dict(color='#3498db', width=2),
                        marker=dict(size=4),
                        hovertemplate=(
                            '<b>Humidity</b><br>'
                            'Time: %{x}<br>'
                            'Humidity: %{y:.1f}%<br>'
                            '<extra></extra>'
                        )
                    ),
                    secondary_y=True
                )
            
            # Update layout
            fig.update_layout(
                title=dict(text=title, x=0.5, font=dict(size=16, weight='bold')),
                height=self.chart_config['default_height'],
                **self.chart_style
            )
            
            # Update y-axes
            fig.update_yaxes(title_text="Temperature (°C)", secondary_y=False)
            fig.update_yaxes(title_text="Humidity (%)", secondary_y=True)
            fig.update_xaxes(title_text="Time")
            
            # Add grid
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)', secondary_y=False)
            
            logger.debug("Combined temperature/humidity chart created")
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create combined chart: {e}")
            return self._create_empty_chart("Error creating combined chart")
    
    def _create_empty_chart(self, message: str) -> go.Figure:
        """Create empty chart with message"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color='gray')
        )
        fig.update_layout(
            height=self.chart_config['default_height'],
            **self.chart_style,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    def _add_temperature_comfort_zone(self, fig: go.Figure, start_time: datetime, end_time: datetime):
        """Add temperature comfort zone to chart"""
        try:
            fig.add_hrect(
                y0=18, y1=26,  # Comfort range 18-26°C
                fillcolor="rgba(46, 204, 113, 0.1)",
                layer="below",
                line_width=0,
                annotation_text="Comfort Zone",
                annotation_position="top left"
            )
        except Exception as e:
            logger.debug(f"Failed to add temperature comfort zone: {e}")
    
    def _add_humidity_comfort_zone(self, fig: go.Figure, start_time: datetime, end_time: datetime):
        """Add humidity comfort zone to chart"""
        try:
            fig.add_hrect(
                y0=30, y1=70,  # Comfort range 30-70%
                fillcolor="rgba(52, 152, 219, 0.1)",
                layer="below",
                line_width=0,
                annotation_text="Comfort Zone",
                annotation_position="top left"
            )
        except Exception as e:
            logger.debug(f"Failed to add humidity comfort zone: {e}")
    
    def _add_battery_warning_zones(self, fig: go.Figure, start_time: datetime, end_time: datetime):
        """Add battery warning zones to chart"""
        try:
            # Critical zone (0-20%)
            fig.add_hrect(
                y0=0, y1=20,
                fillcolor="rgba(231, 76, 60, 0.1)",
                layer="below",
                line_width=0,
                annotation_text="Critical",
                annotation_position="top left"
            )
            
            # Warning zone (20-40%)
            fig.add_hrect(
                y0=20, y1=40,
                fillcolor="rgba(243, 156, 18, 0.1)",
                layer="below",
                line_width=0,
                annotation_text="Low",
                annotation_position="top left"
            )
            
        except Exception as e:
            logger.debug(f"Failed to add battery warning zones: {e}")
    
    def _add_battery_voltage_warning_zones(self, fig: go.Figure, start_time: datetime, end_time: datetime):
        """Add battery voltage warning zones to chart"""
        try:
            # Critical zone (below 3.0V for typical Li-ion batteries)
            fig.add_hrect(
                y0=0, y1=3.0,
                fillcolor="rgba(231, 76, 60, 0.1)",
                layer="below",
                line_width=0,
                annotation_text="Critical",
                annotation_position="top left"
            )
            
            # Warning zone (3.0V - 3.3V)
            fig.add_hrect(
                y0=3.0, y1=3.3,
                fillcolor="rgba(243, 156, 18, 0.1)",
                layer="below",
                line_width=0,
                annotation_text="Low",
                annotation_position="top left"
            )
            
            # Good zone (3.3V - 4.2V)
            fig.add_hrect(
                y0=3.3, y1=4.2,
                fillcolor="rgba(46, 204, 113, 0.1)",
                layer="below",
                line_width=0,
                annotation_text="Good",
                annotation_position="top left"
            )
            
        except Exception as e:
            logger.debug(f"Failed to add battery voltage warning zones: {e}")
    
    def get_chart_info(self) -> Dict[str, Any]:
        """Get information about chart configuration"""
        return {
            'chart_types': ['temperature', 'humidity', 'battery', 'combined'],
            'features': [
                'Multi-location support',
                'Interactive hover tooltips',
                'Comfort/warning zones',
                'Responsive design',
                'Color-coded visualization'
            ],
            'styling': {
                'color_palette': self.color_palette,
                'default_height': self.chart_config['default_height'],
                'responsive': self.chart_config['responsive']
            }
        } 