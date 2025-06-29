# Sensors Dashboard System

A comprehensive IoT monitoring platform that provides real-time visualization of temperature, humidity, and battery data from multiple IoT sensors across different locations. Built with Python, Plotly Dash, and SQLite.

## 🚀 Features

- **Real-time Data Visualization**: Interactive charts for temperature, humidity, and battery data
- **Current Day Focus**: Dashboard defaults to current day data with timezone-aware Pacific/Auckland date handling
- **Multi-location Support**: Monitor sensors across different locations
- **Smart Data Aggregation**: Intelligent aggregation strategies based on time range and data density
- **Professional Chart Scaling**: Fixed Y-axis ranges for consistent visualization (Temperature: 10-30°C, Humidity: 30-100%)
- **Timezone Processing**: Robust Pacific/Auckland timezone conversion with DST handling
- **Responsive Design**: Mobile-first dashboard interface with Bootstrap theme
- **Comprehensive Statistics**: Advanced statistical analysis and comfort indices
- **Error Handling**: Graceful degradation and comprehensive error management

## 📋 Prerequisites

- Python 3.13 or higher
- pipenv (for dependency management)
- SQLite database with sensor data

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sensors_dashboard
   ```

2. **Install dependencies**
   ```bash
   pipenv install
   ```

3. **Verify installation**
   ```bash
   pipenv run python -c "import dash, pandas, pytz, sqlalchemy, dash_bootstrap_components; print('✅ All dependencies installed successfully')"
   ```

## 🗄️ Database Setup

The system expects a SQLite database with the following structure:

### Temperature/Humidity Table (`temp_humidity`)
```sql
CREATE TABLE temp_humidity (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    temperature REAL,
    humidity REAL,
    location TEXT,
    mac TEXT
);
```

### Battery Table (`nano_cell_battery`)
```sql
CREATE TABLE nano_cell_battery (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    voltage REAL,
    percentage REAL,
    dischargerate REAL,
    location TEXT,
    mac TEXT
);
```

### Sample Data
Ensure your database contains sensor data in the expected format. The system will automatically detect available locations and time ranges.

## 🚀 Usage

1. **Start the application**
   ```bash
   pipenv run python app.py
   ```

2. **Access the dashboard**
   Open your browser and navigate to `http://localhost:8050`

3. **Using the dashboard**
   - **Default View**: Dashboard automatically loads current day data in Pacific/Auckland timezone
   - **Date Selection**: Use date picker to select different date ranges (supports single day to multi-day selection)
   - **Location Filtering**: Choose specific locations from the dropdown (defaults to all available locations)
   - **Data Aggregation**: Select aggregation strategy (raw, hourly, daily, weekly, or auto-select)
   - **Chart Analysis**: View interactive charts with fixed Y-axis ranges for consistent comparison
     - Temperature: 10°C to 30°C range
     - Humidity: 30% to 100% range
     - Battery: Auto-scaling based on voltage/percentage data
   - **Statistics**: Real-time statistics cards showing current averages, min/max values, and data point counts

## 🏗️ Architecture Overview

The system follows a layered architecture with clear separation of concerns:

```
sensors_dashboard/
├── app.py                          # Main application entry point
├── src/
│   ├── data/                       # Data processing layer
│   │   ├── aggregation_engine.py   # Smart data aggregation
│   │   ├── database_manager.py     # Database connection management
│   │   ├── statistics_calculator.py # Statistical analysis
│   │   └── timezone_processor.py   # Timezone conversion
│   ├── ui/                         # Presentation layer
│   │   ├── callbacks.py           # Dashboard interactivity
│   │   ├── charts.py              # Chart components
│   │   └── layout.py              # Dashboard layout
│   └── utils/                      # Configuration and utilities
│       ├── config.py              # Application configuration
│       ├── helpers.py             # Utility functions
│       └── logging_setup.py       # Logging configuration
├── database/
│   └── sensors.db                 # SQLite database
└── tests/                         # Test suite
```

### Key Components

#### Data Processing Engine
- **TimezoneProcessor**: Handles UTC ↔ Pacific/Auckland conversions with DST support
- **AggregationEngine**: Smart aggregation with strategy selection (raw, interpolation, hourly, daily, weekly)
- **StatisticsCalculator**: Comprehensive statistical analysis including comfort indices
- **DatabaseManager**: SQLAlchemy-based database access with connection pooling

#### Dashboard Interface
- **DashboardLayout**: Responsive layout with Bootstrap theme and timezone-aware current day defaults
- **ChartComponents**: Interactive Plotly charts with professional fixed Y-axis scaling
- **DashboardCallbacks**: Real-time data updates, timezone conversion, and user interaction handling

#### Configuration System
- **Config**: Centralized configuration management
- **LoggingSetup**: Structured logging with configurable levels
- **Helpers**: Utility functions for data processing

## 🔧 Configuration

### Environment Variables
The system uses the following configuration (see `src/utils/config.py`):

```python
# Database Configuration
DATABASE_PATH = "database/sensors.db"

# Application Configuration
HOST = "0.0.0.0"
PORT = 8050
DEBUG = True

# Timezone Configuration
TIMEZONE = "Pacific/Auckland"

# Performance Configuration
CACHE_TIMEOUT = 300  # 5 minutes
MAX_CONNECTIONS = 10
```

### Customization
To modify the system for your needs:

1. **Database Schema**: Update table structures in `src/data/database_manager.py`
2. **Timezone**: Change timezone in `src/utils/config.py`
3. **Charts**: Modify chart components in `src/ui/charts.py` (includes fixed Y-axis ranges for consistency)
4. **Layout**: Customize dashboard layout in `src/ui/layout.py`
5. **Aggregation**: Add new aggregation strategies in `src/data/aggregation_engine.py`

## 📊 Data Processing

### Aggregation Strategies
The system automatically selects the best aggregation strategy based on time range:

- **Raw**: No aggregation (for short time ranges)
- **Interpolation**: For sparse data with gaps
- **Hourly**: Average data by hour
- **Daily**: Average data by day
- **Weekly**: Average data by week

### Timezone Processing
All timestamps are stored in UTC and converted to Pacific/Auckland timezone for display. The system handles:
- **Current Day Detection**: Dashboard defaults to current day in Pacific/Auckland timezone
- **Automatic UTC Conversion**: Local date selections converted to UTC for database queries
- **Daylight Saving Time transitions**: Robust DST handling with pytz library
- **Timezone validation**: Comprehensive timezone boundary and edge case handling
- **Graceful error handling**: Fallback mechanisms for invalid timestamps

### Statistics Calculation
The system provides comprehensive statistics:
- Basic statistics (min, max, mean, std, quartiles)
- Temperature/humidity comfort indices
- Battery health indicators
- Trend analysis

## 🧪 Testing

Run the test suite:
```bash
pipenv run python -m pytest tests/
```

Run linting:
```bash
pipenv run ruff check .
```

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure the database file exists in `database/sensors.db`
   - Check file permissions
   - Verify SQLite is installed

2. **Import Errors**
   - Ensure you're using pipenv: `pipenv run python app.py`
   - Verify all dependencies are installed: `pipenv install`

3. **Timezone Issues**
   - Check timezone configuration in `src/utils/config.py`
   - Ensure pytz is properly installed

4. **Chart Display Issues**
   - Check browser console for JavaScript errors
   - Verify data exists for selected time range and location

### Debugging
For debugging, run the application with logging:
```bash
pipenv run python app.py > app.log 2>&1
```

Then inspect the log file:
```bash
tail -f app.log
```

## 🚀 Deployment

### Production Deployment
For production deployment:

1. **Update configuration**
   ```python
   DEBUG = False
   HOST = "0.0.0.0"
   PORT = 80  # or your preferred port
   ```

2. **Set up reverse proxy** (nginx recommended)
3. **Configure SSL certificates**
4. **Set up monitoring and logging**

### Docker Deployment
Create a `Dockerfile`:
```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install pipenv
RUN pipenv install --system --deploy

EXPOSE 8050
CMD ["python", "app.py"]
```

## 📈 Performance Optimization

### Caching
The system implements multi-level caching:
- Database query caching
- Aggregation result caching
- Chart component caching

### Database Optimization
- Connection pooling for database connections
- Optimized queries with proper indexing
- Parameterized queries for security

### Frontend Optimization
- Lazy loading of chart components
- Efficient data updates
- Responsive design for mobile devices

## 🔒 Security Considerations

- Input validation for all user inputs
- SQL injection prevention through parameterized queries
- XSS protection through proper data sanitization
- CORS configuration for production deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📝 License

[Add your license information here]

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the architecture documentation
3. Open an issue on GitHub

## 🔄 Version History

- **v1.1.0**: Enhanced user experience (2025-06-29)
  - **Current Day Default**: Date picker defaults to current day in Pacific/Auckland timezone
  - **Professional Chart Scaling**: Fixed Y-axis ranges (Temperature: 10-30°C, Humidity: 30-100%)
  - **Improved Usability**: Automatic current data loading without manual selection
  - **Enhanced Documentation**: Comprehensive documentation updates

- **v1.0.0**: Initial release with core functionality
  - Real-time data visualization
  - Multi-location support
  - Smart aggregation
  - Timezone processing

---

**Note**: This system is designed for IoT sensor monitoring and can be extended for various sensor types and use cases. The modular architecture makes it easy to add new features and customize for specific requirements. 