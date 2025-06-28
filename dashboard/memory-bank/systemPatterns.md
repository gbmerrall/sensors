# SYSTEM PATTERNS: Sensors Dashboard System

## Architectural Patterns

### Primary Pattern: Layered Architecture
The system follows a strict layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────┐
│         Presentation Layer          │
│    (Dash Components, Callbacks)     │
├─────────────────────────────────────┤
│        Business Logic Layer        │
│  (Data Processing, Aggregation)    │
├─────────────────────────────────────┤
│        Data Access Layer           │
│   (SSH Manager, Query Builder)     │
├─────────────────────────────────────┤
│        Infrastructure Layer        │
│    (Database, Caching, Config)     │
└─────────────────────────────────────┘
```

### Supporting Patterns

#### 1. Model-View-Controller (MVC)
- **Model**: Data processing and business logic components
- **View**: Dash layout and visualization components  
- **Controller**: Dash callbacks and event handlers

#### 2. Repository Pattern
- **Database Repository**: Abstracts database access through SSH connections
- **Cache Repository**: Manages cached data with LRU eviction
- **Query Repository**: Builds and executes optimized queries

#### 3. Strategy Pattern
- **Aggregation Strategy**: Pluggable aggregation methods (interpolation vs averaging)
- **Timezone Strategy**: Different timezone conversion strategies
- **Caching Strategy**: Various caching approaches based on data type

#### 4. Observer Pattern
- **Data Updates**: UI components observe data changes
- **Status Updates**: Loading states and error conditions
- **Refresh Events**: Manual and automatic refresh mechanisms

## Design Patterns

### Data Processing Patterns

#### 1. Pipeline Pattern
Data flows through processing pipeline:
```
Raw Data → Timezone Conversion → Aggregation → Caching → Visualization
```

#### 2. Factory Pattern  
- **Chart Factory**: Creates different chart types based on data
- **Query Factory**: Builds queries based on parameters
- **Processor Factory**: Creates appropriate data processors

#### 3. Decorator Pattern
- **Caching Decorator**: Adds caching to data retrieval functions
- **Timing Decorator**: Adds performance monitoring
- **Error Handling Decorator**: Adds error handling to operations

### UI Patterns

#### 1. Component Pattern
- **Reusable Components**: Statistics boxes, chart containers, control panels
- **Composite Components**: Dashboard composed of smaller components
- **Container Components**: Manage state and data flow

#### 2. State Management Pattern
- **Centralized State**: Dash callback state management
- **Local State**: Component-specific state (selections, filters)
- **Derived State**: Computed values from base state

## Technology Choices and Rationales

### Framework: Plotly Dash
**Rationale**: 
- Python-native web framework ideal for data visualization
- Built-in support for interactive charts and real-time updates
- Excellent integration with pandas and plotly
- Callback system perfect for reactive UI updates

### Data Processing: Pandas
**Rationale**:
- Industry standard for data manipulation in Python
- Excellent time series support for sensor data
- Built-in aggregation and resampling functions
- Efficient memory usage for large datasets

### Database Access: SQLAlchemy + SSH
**Rationale**:
- SQLAlchemy provides database abstraction
- SSH tunneling required for secure remote access
- Connection pooling for performance optimization
- Parameterized queries for security

### Caching: Custom LRU Implementation
**Rationale**:
- Sensor data has temporal locality (recent data accessed frequently)
- LRU eviction matches access patterns
- Custom implementation allows fine-tuning for sensor data
- 5-minute TTL balances freshness with performance

### Timezone Handling: pytz
**Rationale**:
- Comprehensive timezone database
- Handles daylight saving time transitions
- Industry standard for Python timezone handling
- Pacific/Auckland timezone support required

## Architectural Decisions

### Decision 1: Single-Page Application
**Context**: Need responsive, interactive dashboard
**Decision**: Build as SPA with Dash
**Consequences**: Better user experience, more complex state management
**Alternatives Considered**: Multi-page application, separate frontend

### Decision 2: Server-Side Data Processing
**Context**: Large datasets, complex aggregations
**Decision**: Process data on server before sending to client
**Consequences**: Reduced network traffic, server resource usage
**Alternatives Considered**: Client-side processing, hybrid approach

### Decision 3: SSH Tunnel for Database Access
**Context**: Database on remote server, security requirements
**Decision**: Use SSH tunnel for all database connections
**Consequences**: Added complexity, secure access, connection management overhead
**Alternatives Considered**: Direct database connection, VPN access

### Decision 4: Intelligent Caching Strategy
**Context**: Performance requirements, data freshness needs
**Decision**: Multi-level caching with 5-minute TTL
**Consequences**: Improved performance, cache invalidation complexity
**Alternatives Considered**: No caching, simple time-based caching

### Decision 5: Responsive Design First
**Context**: Multi-device usage requirements
**Decision**: Mobile-first responsive design using Bootstrap
**Consequences**: Better mobile experience, increased CSS complexity
**Alternatives Considered**: Desktop-only, separate mobile app

## Implementation Patterns

### Error Handling Pattern
```python
def with_error_handling(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DatabaseError as e:
            log_error(e)
            return error_response("Database connection failed")
        except ProcessingError as e:
            log_error(e)
            return error_response("Data processing failed")
    return wrapper
```

### Caching Pattern
```python
@cache_result(ttl=300, key_func=lambda *args: generate_cache_key(args))
def get_sensor_data(location, start_time, end_time, aggregation):
    # Data retrieval and processing logic
    pass
```

### Configuration Pattern
```python
class Config:
    SSH_HOST = '192.168.86.250'
    SSH_USER = 'graeme' 
    DEFAULT_LOCATION = 'wine'
    TIMEZONE = 'Pacific/Auckland'
    CACHE_TTL = 300
    CACHE_MAX_SIZE = 100
```

### Component Structure Pattern
```python
def create_dashboard_layout():
    return html.Div([
        create_header(),
        create_control_panel(),
        create_statistics_row(),
        create_charts_section(),
        create_footer()
    ])
```

## Quality Attributes Implementation

### Performance
- **Data Aggregation**: Pandas optimized operations
- **Caching**: Multi-level caching with LRU eviction
- **Query Optimization**: Indexed queries, connection pooling
- **Lazy Loading**: Load data only when needed

### Scalability  
- **Horizontal**: Multiple dashboard instances
- **Vertical**: Connection pooling, efficient algorithms
- **Data**: Pagination for large datasets

### Maintainability
- **Modular Design**: Clear separation of concerns
- **Configuration**: External configuration files
- **Testing**: Comprehensive unit and integration tests
- **Documentation**: Inline documentation and architectural docs

### Reliability
- **Error Handling**: Comprehensive error handling at all layers
- **Retry Logic**: Automatic retry for transient failures
- **Fallback**: Graceful degradation when services unavailable
- **Monitoring**: Performance and error monitoring

### Security
- **SSH Tunneling**: Encrypted database connections
- **Input Validation**: Sanitize all user inputs
- **Access Control**: Authentication and authorization
- **Audit Logging**: Track all data access operations

## Cross-Cutting Concerns

### Logging
- **Structured Logging**: JSON format for easy parsing
- **Log Levels**: DEBUG, INFO, WARN, ERROR with appropriate usage
- **Performance Logging**: Track query times and processing duration
- **Error Logging**: Detailed error context and stack traces

### Configuration Management
- **Environment-Based**: Different configs for dev/test/prod
- **External Files**: Configuration separate from code
- **Validation**: Validate configuration on startup
- **Hot Reload**: Support configuration changes without restart

### Monitoring and Observability
- **Performance Metrics**: Response times, query duration, cache hit rates
- **Health Checks**: Database connectivity, service availability
- **User Analytics**: Usage patterns, popular features
- **Error Tracking**: Error rates, failure patterns

This system patterns document establishes the architectural foundation for implementing a robust, scalable, and maintainable sensors dashboard system.
