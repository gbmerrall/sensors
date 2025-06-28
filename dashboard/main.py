#!/usr/bin/env python3
"""
Sensors Dashboard Main Application

Entry point for the IoT sensors dashboard system providing real-time
visualization of temperature, humidity, and battery data from multiple locations.
"""

import dash
import dash_bootstrap_components as dbc
from src.utils.logging_setup import setup_logging
from src.utils.config import Config
from src.ui.layout import DashboardLayout
from src.ui.callbacks import DashboardCallbacks

# Initialize logging
logger = setup_logging()

# Initialize Dash app with Bootstrap theme and Font Awesome
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
    ],
    suppress_callback_exceptions=True,
    title="Sensors Dashboard",
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "description", "content": "IoT Sensors Dashboard - Real-time monitoring"}
    ]
)

# Initialize dashboard layout
dashboard_layout = DashboardLayout()

# Set the app layout
app.layout = dashboard_layout.create_main_layout()

# Initialize callback functions
dashboard_callbacks = DashboardCallbacks(app)

# Expose server for deployment
server = app.server

if __name__ == "__main__":
    logger.info("Starting Sensors Dashboard Application")
    logger.info(f"Configuration: {Config.get_all_settings()}")
    logger.info("Dashboard callbacks initialized - Application ready")
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT) 