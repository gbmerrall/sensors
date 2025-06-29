"""
Dashboard Layout Components

Implements the responsive dashboard layout with adaptive grid structure
as designed in the UI/UX creative phase.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from typing import Dict, Any
from src.utils.logging_setup import get_ui_logger
from datetime import date, datetime
import pytz
from src.utils.config import Config

logger = get_ui_logger()


class DashboardLayout:
    """
    Main dashboard layout manager
    
    Implements the Adaptive Grid Layout from the creative phase with
    mobile-first responsive design and consistent styling.
    """
    
    def __init__(self):
        """Initialize dashboard layout manager"""
        self.app_title = "🌡️ Sensors Dashboard"
        self.brand_color = "#2c3e50"
        self.accent_color = "#3498db"
        
        # Get current date in Pacific/Auckland timezone
        self.local_tz = pytz.timezone(Config.DEFAULT_TIMEZONE)
        self.current_date = date.today()  # Will be replaced with timezone-aware date
        self._set_current_date()
        
        logger.info("Dashboard layout manager initialized")
    
    def _set_current_date(self):
        """Set current date in Pacific/Auckland timezone"""
        try:
            utc_now = datetime.now(pytz.UTC)
            local_now = utc_now.astimezone(self.local_tz)
            self.current_date = local_now.date()
            logger.debug(f"Current date set to: {self.current_date} (Pacific/Auckland)")
        except Exception as e:
            logger.warning(f"Failed to set timezone-aware date, using system date: {e}")
            self.current_date = date.today()
    
    def create_header(self) -> dbc.Row:
        """
        Create responsive header with navigation
        
        Returns:
            Bootstrap row with header content
        """
        try:
            header = dbc.Row([
                dbc.Col([
                    dbc.Navbar([
                        dbc.Container([
                            dbc.NavbarBrand([
                                html.I(className="fas fa-thermometer-half me-2"),
                                self.app_title
                            ], className="fw-bold text-white")
                        ], fluid=True)
                    ], color=self.brand_color, dark=True, className="mb-4")
                ], width=12)
            ])
            
            logger.debug("Header created successfully")
            return header
            
        except Exception as e:
            logger.error(f"Failed to create header: {e}")
            return dbc.Row([])
    
    def create_control_panel(self) -> dbc.Card:
        """
        Create control panel with filters and settings
        
        Returns:
            Bootstrap card with control panel content
        """
        try:
            control_panel = dbc.Card([
                dbc.CardHeader([
                    html.H5([
                        html.I(className="fas fa-sliders-h me-2"),
                        "Control Panel"
                    ], className="mb-0")
                ]),
                dbc.CardBody([
                    dbc.Row([
                        # Date Range Selection
                        dbc.Col([
                            html.Label("Date Range:", className="fw-bold mb-2"),
                            dcc.DatePickerRange(
                                id='date-range-picker',
                                start_date_placeholder_text="Start Date",
                                end_date_placeholder_text="End Date",
                                display_format='DD/MM/YYYY',
                                style={'width': '100%'},
                                className="mb-3",
                                minimum_nights=0,  # Allow same day selection
                                clearable=True,
                                with_portal=False,
                                updatemode='singledate',  # Allow independent date selection
                                start_date=self.current_date.isoformat(),  # Use Pacific/Auckland current date
                                end_date=self.current_date.isoformat()     # Use Pacific/Auckland current date
                            )
                        ], xs=12, sm=6, lg=3),
                        
                        # Location Selection
                        dbc.Col([
                            html.Label("Location:", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id='location-dropdown',
                                options=[],  # Will be populated dynamically
                                value=None,
                                placeholder="Select location(s)",
                                multi=True,
                                className="mb-3"
                            )
                        ], xs=12, sm=6, lg=3),
                        
                        # Aggregation Method
                        dbc.Col([
                            html.Label("Data View:", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id='aggregation-dropdown',
                                options=[
                                    {'label': 'Raw Data', 'value': 'raw'},
                                    {'label': 'Hourly Average', 'value': 'hourly'},
                                    {'label': 'Daily Average', 'value': 'daily'},
                                    {'label': 'Auto Select', 'value': 'auto'}
                                ],
                                value='auto',
                                placeholder="Select aggregation",
                                className="mb-3"
                            )
                        ], xs=12, sm=6, lg=3),
                        
                        # Refresh Button
                        dbc.Col([
                            html.Label("Actions:", className="fw-bold mb-2"),
                            dbc.ButtonGroup([
                                dbc.Button([
                                    html.I(className="fas fa-sync-alt me-1"),
                                    "Refresh"
                                ], id="refresh-button", color="primary", size="sm"),
                                dbc.Button([
                                    html.I(className="fas fa-download me-1"),
                                    "Export"
                                ], id="export-button", color="secondary", size="sm")
                            ], className="d-flex w-100")
                        ], xs=12, sm=6, lg=3)
                    ])
                ])
            ], className="mb-4")
            
            logger.debug("Control panel created successfully")
            return control_panel
            
        except Exception as e:
            logger.error(f"Failed to create control panel: {e}")
            return dbc.Card([])
    
    def create_statistics_cards(self) -> dbc.Row:
        """
        Create statistics summary cards
        
        Returns:
            Bootstrap row with statistics cards
        """
        try:
            stats_cards = dbc.Row([
                # Temperature Stats
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-thermometer-half fa-2x text-danger mb-2"),
                                html.H4("--°C", id="temp-avg", className="mb-1"),
                                html.P("Avg Temperature", className="text-muted mb-0"),
                                html.Small("Min: --°C | Max: --°C", id="temp-range", className="text-muted")
                            ], className="text-center")
                        ])
                    ], className="h-100 border-start border-danger border-4")
                ], xs=12, sm=6, lg=3),
                
                # Humidity Stats
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-tint fa-2x text-info mb-2"),
                                html.H4("--%", id="humidity-avg", className="mb-1"),
                                html.P("Avg Humidity", className="text-muted mb-0"),
                                html.Small("Min: --% | Max: --%", id="humidity-range", className="text-muted")
                            ], className="text-center")
                        ])
                    ], className="h-100 border-start border-info border-4")
                ], xs=12, sm=6, lg=3),
                
                # Battery Stats
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-battery-three-quarters fa-2x text-success mb-2"),
                                html.H4("--%", id="battery-avg", className="mb-1"),
                                html.P("Avg Battery", className="text-muted mb-0"),
                                html.Small("Min: --% | Max: --%", id="battery-range", className="text-muted")
                            ], className="text-center")
                        ])
                    ], className="h-100 border-start border-success border-4")
                ], xs=12, sm=6, lg=3),
                
                # Data Points Stats
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-database fa-2x text-warning mb-2"),
                                html.H4("--", id="data-points", className="mb-1"),
                                html.P("Data Points", className="text-muted mb-0"),
                                html.Small("Last updated: --", id="last-updated", className="text-muted")
                            ], className="text-center")
                        ])
                    ], className="h-100 border-start border-warning border-4")
                ], xs=12, sm=6, lg=3)
            ], className="mb-4")
            
            logger.debug("Statistics cards created successfully")
            return stats_cards
            
        except Exception as e:
            logger.error(f"Failed to create statistics cards: {e}")
            return dbc.Row([])
    
    def create_chart_area(self) -> dbc.Row:
        """
        Create chart display area with responsive grid
        
        Returns:
            Bootstrap row with chart containers
        """
        try:
            chart_area = dbc.Row([
                # Temperature Chart
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5([
                                html.I(className="fas fa-thermometer-half me-2 text-danger"),
                                "Temperature"
                            ], className="mb-0")
                        ]),
                        dbc.CardBody([
                            dcc.Loading(
                                id="temperature-loading",
                                children=[
                                    dcc.Graph(
                                        id="temperature-chart",
                                        config={'displayModeBar': True},
                                        style={'height': '400px'}
                                    )
                                ],
                                type="default"
                            )
                        ])
                    ], className="mb-4")
                ], xs=12, lg=6),
                
                # Humidity Chart
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5([
                                html.I(className="fas fa-tint me-2 text-info"),
                                "Humidity"
                            ], className="mb-0")
                        ]),
                        dbc.CardBody([
                            dcc.Loading(
                                id="humidity-loading",
                                children=[
                                    dcc.Graph(
                                        id="humidity-chart",
                                        config={'displayModeBar': True},
                                        style={'height': '400px'}
                                    )
                                ],
                                type="default"
                            )
                        ])
                    ], className="mb-4")
                ], xs=12, lg=6),
                
                # Battery Chart (full width)
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5([
                                html.I(className="fas fa-battery-three-quarters me-2 text-success"),
                                "Battery Voltage"
                            ], className="mb-0")
                        ]),
                        dbc.CardBody([
                            dcc.Loading(
                                id="battery-loading",
                                children=[
                                    dcc.Graph(
                                        id="battery-chart",
                                        config={'displayModeBar': True},
                                        style={'height': '400px'}
                                    )
                                ],
                                type="default"
                            )
                        ])
                    ], className="mb-4")
                ], xs=12)
            ])
            
            logger.debug("Chart area created successfully")
            return chart_area
            
        except Exception as e:
            logger.error(f"Failed to create chart area: {e}")
            return dbc.Row([])
    
    def create_footer(self) -> dbc.Row:
        """
        Create dashboard footer
        
        Returns:
            Bootstrap row with footer content
        """
        try:
            footer = dbc.Row([
                dbc.Col([
                    html.Hr(),
                    html.Div([
                        html.P([
                            "Sensors Dashboard System | ",
                            html.A("Documentation", href="#", className="text-decoration-none"),
                            " | ",
                            html.A("Support", href="#", className="text-decoration-none")
                        ], className="text-center text-muted mb-0")
                    ])
                ], width=12)
            ], className="mt-4")
            
            logger.debug("Footer created successfully")
            return footer
            
        except Exception as e:
            logger.error(f"Failed to create footer: {e}")
            return dbc.Row([])
    
    def create_main_layout(self) -> dbc.Container:
        """
        Create the complete main dashboard layout
        
        Returns:
            Bootstrap container with complete layout
        """
        try:
            layout = dbc.Container([
                # Header
                self.create_header(),
                
                # Control Panel
                self.create_control_panel(),
                
                # Statistics Cards
                self.create_statistics_cards(),
                
                # Chart Area
                self.create_chart_area(),
                
                # Footer
                self.create_footer(),
                
                # Hidden components for data storage
                dcc.Store(id='sensor-data-store'),
                dcc.Store(id='location-data-store'),
                dcc.Interval(
                    id='auto-refresh-interval',
                    interval=300*1000,  # 5 minutes
                    n_intervals=0,
                    disabled=True
                )
            ], fluid=True, className="py-3")
            
            logger.info("Main dashboard layout created successfully")
            return layout
            
        except Exception as e:
            logger.error(f"Failed to create main layout: {e}")
            return dbc.Container([html.H1("Error creating dashboard layout")])
    
    def get_layout_info(self) -> Dict[str, Any]:
        """
        Get information about the current layout structure
        
        Returns:
            Dictionary with layout information
        """
        return {
            'layout_type': 'Adaptive Grid Layout',
            'responsive_breakpoints': ['xs (mobile)', 'sm (tablet)', 'lg (desktop)'],
            'components': [
                'Header with navigation',
                'Control panel with filters',
                'Statistics summary cards',
                'Chart display area',
                'Footer'
            ],
            'styling_framework': 'Bootstrap 5',
            'icons': 'Font Awesome',
            'chart_library': 'Plotly Dash'
        } 