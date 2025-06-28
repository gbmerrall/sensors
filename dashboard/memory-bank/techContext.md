# TECHNICAL CONTEXT: Sensors Dashboard System

## Technology Stack Overview

### Core Technologies
- **Python 3.13**: Latest Python version with improved performance and features
- **Plotly Dash 3.0+**: Modern Python web framework for data visualization applications
- **Pandas 2.0+**: High-performance data manipulation and analysis library
- **SQLAlchemy**: Python SQL toolkit and Object-Relational Mapping (ORM) library
- **pytz 2023.3+**: Comprehensive timezone calculations for Python
- **pipenv**: Python dependency management and virtual environment tool

### Infrastructure Technologies
- **SQLite Database**: Existing database with sensor data (sensors.db)
- **SSH Connection**: Secure connection to remote database server (192.168.86.250)
- **paramiko/asyncssh**: SSH client library for Python database connections

### Development and Testing
- **pytest**: Testing framework for unit and integration tests
- **ruff**: Fast Python linter and code formatter
- **Werkzeug**: WSGI utility library (Dash dependency)

## Technical Architecture

### System Architecture Layers

#### 1. Presentation Layer (Web Interface)
```python
# Technology: Plotly Dash + HTML/CSS/JavaScript
# Components:
- Dashboard layout management
- Interactive charts and visualizations  
- Control panels (date pickers, selectors)
- Statistics display boxes
- Responsive design with Bootstrap CSS
```

#### 2. Business Logic Layer (Data Processing)
```python
# Technology: Pandas + Custom Processing Logic
# Components:
- Data aggregation algorithms (interpolation vs averaging)
- Timezone conversion utilities (UTC ↔ Pacific/Auckland)
- Multi-location data processing
- Statistics calculation engine
- Caching and performance optimization
```

#### 3. Data Access Layer (Database Interface)
```python
# Technology: SQLAlchemy + SSH Tunneling
# Components:
- SSH connection management
- Database query builder
- Connection pooling
- Query result processing
- Error handling and retry logic
```

#### 4. Infrastructure Layer (System Services)
```python
# Technology: Python Standard Library + External Services
# Components:
- Configuration management
- Logging and monitoring
- Cache management (LRU with TTL)
- Error handling and reporting
```

## Database Schema and Access

### Existing Database Structure
```sql
-- Temperature and Humidity Data
CREATE TABLE temp_humidity (
    location VARCHAR(64) NOT NULL,
    mac VARCHAR(64) NOT NULL,
    temperature NUMERIC NOT NULL,
    humidity NUMERIC NOT NULL,
    timestamp DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
    PRIMARY KEY (location, timestamp)
);

-- Battery Data
CREATE TABLE nano_cell_battery (
    location VARCHAR(64) NOT NULL,
    mac VARCHAR(64) NOT NULL,
    voltage NUMERIC NOT NULL,
    percentage NUMERIC NOT NULL,
    dischargerate NUMERIC NOT NULL,
    timestamp DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
    PRIMARY KEY (location, timestamp)
);
```

### Database Access Pattern
```python
# SSH Tunnel + SQLAlchemy Connection
ssh_tunnel = SSHTunnelForwarder(
    ('192.168.86.250', 22),
    ssh_username='graeme',
    ssh_private_key='~/.ssh/id_ed25519',
    remote_bind_address=('localhost', 3306)
)

engine = create_engine(f'sqlite:///path/to/sensors.db')
```

## Data Processing Architecture

### Timezone Processing
```python
# Pacific/Auckland ↔ UTC Conversion
from pytz import timezone

pacific_tz = timezone('Pacific/Auckland')
utc_tz = timezone('UTC')

# Convert user input (Pacific/Auckland) to UTC for database queries
# Convert database results (UTC) to Pacific/Auckland for display
```

### Aggregation Strategies
```python
# 15-minute Interpolation (for short time periods)
df_resampled = df.resample('15min').interpolate(method='linear')

# Time-based Averaging (for longer periods)
aggregation_periods = {
    '1hr': df.resample('1H').mean(),
    '2hr': df.resample('2H').mean(),
    '6hr': df.resample('6H').mean(),
    '12hr': df.resample('12H').mean(),
    '1day': df.resample('1D').mean()
}
```

### Caching Implementation
```python
# LRU Cache with TTL
from functools import lru_cache
import time

class TTLCache:
    def __init__(self, maxsize=100, ttl=300):
        self.cache = {}
        self.maxsize = maxsize
        self.ttl = ttl
    
    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
```

## User Interface Technology

### Dash Component Architecture
```python
import dash
from dash import html, dcc, Input, Output, callback
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

# Layout Structure
app.layout = dbc.Container([
    # Header with title and navigation
    dbc.Row([
        dbc.Col([
            html.H1("Sensors Dashboard"),
            html.Hr()
        ])
    ]),
    
    # Control Panel
    dbc.Row([
        dbc.Col([
            # Date range picker
            dcc.DatePickerRange(id='date-range'),
            # Location selector
            dcc.Dropdown(id='location-selector'),
            # Aggregation selector  
            dcc.Dropdown(id='aggregation-selector'),
            # Refresh button
            dbc.Button("Refresh", id="refresh-btn")
        ])
    ]),
    
    # Statistics Boxes
    dbc.Row([
        dbc.Col([
            create_stats_box("Temperature Stats")
        ], width=6),
        dbc.Col([
            create_stats_box("Humidity Stats")  
        ], width=6)
    ]),
    
    # Charts
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='temperature-chart')
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='humidity-chart')
        ])
    ])
])
```

### Chart Configuration
```python
# Temperature Chart Configuration
temperature_chart = go.Figure()
temperature_chart.add_trace(go.Scatter(
    x=df['timestamp'],
    y=df['temperature'],
    mode='lines+markers',
    name=location,
    line=dict(width=2),
    marker=dict(size=4)
))

temperature_chart.update_layout(
    title="Temperature Over Time",
    xaxis_title="Time (Pacific/Auckland)",
    yaxis_title="Temperature (°C)",
    hovermode='x unified',
    showlegend=True
)
```

## Performance Optimization

### Query Optimization
```python
# Optimized query with proper indexing
SELECT location, temperature, humidity, timestamp
FROM temp_humidity 
WHERE location IN ('wine', 'garage', 'office')
  AND timestamp BETWEEN '2023-01-01 00:00:00' AND '2023-01-02 00:00:00'
ORDER BY timestamp ASC;

# Index recommendations
CREATE INDEX idx_temp_humidity_location ON temp_humidity(location);
CREATE INDEX idx_temp_humidity_timestamp ON temp_humidity(timestamp);
CREATE INDEX idx_temp_humidity_location_timestamp ON temp_humidity(location, timestamp);
```

### Connection Pooling
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'sqlite:///sensors.db',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

### Memory Management
```python
# Efficient data processing with chunking
def process_large_dataset(query, chunk_size=10000):
    for chunk in pd.read_sql(query, engine, chunksize=chunk_size):
        yield process_chunk(chunk)
```

## Security Considerations

### SSH Security
```python
# SSH Key Authentication
ssh_config = {
    'ssh_host': '192.168.86.250',
    'ssh_username': 'graeme',
    'ssh_private_key': os.path.expanduser('~/.ssh/id_ed25519'),
    'ssh_port': 22
}

# Connection validation
def validate_ssh_connection(config):
    try:
        with SSHTunnelForwarder(**config) as tunnel:
            return tunnel.is_alive
    except Exception as e:
        logger.error(f"SSH connection failed: {e}")
        return False
```

### Input Validation
```python
# Sanitize user inputs
def validate_date_range(start_date, end_date):
    if not isinstance(start_date, datetime):
        raise ValueError("Invalid start date format")
    if not isinstance(end_date, datetime):
        raise ValueError("Invalid end date format")
    if start_date >= end_date:
        raise ValueError("Start date must be before end date")
    return True

def validate_location(location):
    allowed_locations = ['wine', 'garage', 'office', 'bedroom']
    if location not in allowed_locations:
        raise ValueError(f"Invalid location: {location}")
    return True
```

## Development Environment

### Environment Setup
```bash
# Install pipenv
pip install pipenv

# Create virtual environment and install dependencies
pipenv install

# Install development dependencies
pipenv install --dev

# Activate environment
pipenv shell

# Run application
python app.py
```

### Configuration Management
```python
# config/settings.py
import os
from dataclasses import dataclass

@dataclass
class Config:
    # SSH Configuration
    SSH_HOST: str = '192.168.86.250'
    SSH_USER: str = 'graeme'
    SSH_KEY_PATH: str = '~/.ssh/id_ed25519'
    
    # Database Configuration
    DATABASE_PATH: str = 'database/sensors.db'
    DEFAULT_LOCATION: str = 'wine'
    
    # Application Configuration
    TIMEZONE: str = 'Pacific/Auckland'
    CACHE_TTL: int = 300  # 5 minutes
    CACHE_MAX_SIZE: int = 100
    
    # UI Configuration
    REFRESH_INTERVAL: int = 30000  # 30 seconds
    MAX_DATA_POINTS: int = 1000
    
    @classmethod
    def from_env(cls):
        return cls(
            SSH_HOST=os.getenv('SSH_HOST', cls.SSH_HOST),
            SSH_USER=os.getenv('SSH_USER', cls.SSH_USER),
            # ... other environment variables
        )
```

### Testing Framework
```python
# tests/conftest.py
import pytest
import pandas as pd
from unittest.mock import Mock

@pytest.fixture
def sample_sensor_data():
    return pd.DataFrame({
        'location': ['wine'] * 100,
        'temperature': range(20, 120),
        'humidity': range(30, 130),
        'timestamp': pd.date_range('2023-01-01', periods=100, freq='1H')
    })

@pytest.fixture
def mock_ssh_connection():
    mock = Mock()
    mock.is_alive = True
    return mock

# tests/test_data_processing.py
def test_timezone_conversion(sample_sensor_data):
    processor = TimezoneProcessor()
    converted = processor.utc_to_pacific(sample_sensor_data)
    assert 'timestamp' in converted.columns
    assert len(converted) == len(sample_sensor_data)
```

## Deployment Considerations

### Production Configuration
```python
# Production settings
PRODUCTION_CONFIG = {
    'debug': False,
    'host': '0.0.0.0',
    'port': 8050,
    'threaded': True,
    'processes': 1
}

# Development settings
DEVELOPMENT_CONFIG = {
    'debug': True,
    'host': '127.0.0.1', 
    'port': 8050,
    'dev_tools_hot_reload': True
}
```

### Monitoring and Logging
```python
import logging
import structlog

# Configure structured logging
logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

logger = structlog.get_logger()

# Performance monitoring
def monitor_performance(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        logger.info("function_executed", 
                   function=func.__name__, 
                   duration=duration)
        return result
    return wrapper
```

This technical context provides the foundation for implementing a robust, scalable sensors dashboard system using modern Python technologies and best practices.
