# Sensors Server

A FastAPI-based server for collecting and storing sensor data from IoT devices. The server accepts temperature/humidity readings and power status data, validates inputs, and stores them in a SQLite database with location mapping from sensor MAC addresses.

## Features

- **FastAPI Framework**: Modern, fast web framework with automatic API documentation
- **Input Validation**: Comprehensive validation of MAC addresses, data types, and ranges
- **Database Storage**: SQLite database with proper schema for sensor data
- **Location Mapping**: Automatic location assignment based on sensor MAC addresses
- **Error Handling**: Proper HTTP status codes and error messages
- **Logging**: Structured logging for debugging and monitoring
- **API Documentation**: Automatic OpenAPI/Swagger documentation
- **Testing**: Both Python and cURL test scripts included

## Setup Instructions

1. **Install dependencies using pipenv:**
   ```bash
   pipenv install
   ```

2. **Activate the virtual environment:**
   ```bash
   pipenv shell
   ```

3. **Run the application:**
   ```bash
   python run.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Access the API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### 1. `/connection` (GET)
Simple connection test endpoint that returns only a 200 status code.

### 2. `/` (GET)
Root endpoint that returns "Hello world" as plain text.

### 3. `/reload-locations` (GET)
Reloads the sensor configuration from `external/sensors.json` for the application to read.

**Response:**
```json
{
    "message": "Sensor configuration reloaded successfully",
    "status": "success"
}
```

### 4. `/temperature` (POST)
Accepts temperature and humidity data from sensors.

**Request Body:**
```json
{
    "mac": "dd:cc:bb:aa:99:88",
    "temperature": 23.2,
    "humidity": 50.6,
    "timestamp": "2024-07-18T02:44:22+00:00"
}
```

**Validation Rules:**
- MAC address must be in full 6-byte format: `xx:xx:xx:xx:xx:xx`
- Temperature must be between -50 and 100 degrees
- Humidity must be between 0 and 100 percent
- Timestamp is optional (uses current time from server if not provided)

### 5. `/powerstatus` (POST)
Accepts power status data from sensors.

**Request Body:**
```json
{
    "mac": "dd:cc:bb:aa:99:88",
    "voltage": 23.2,
    "percentage": 89.2,
    "dischargerate": 55,
    "timestamp": "2024-07-18T02:44:22+00:00"
}
```

**Validation Rules:**
- MAC address must be in full 6-byte format: `xx:xx:xx:xx:xx:xx`
- Voltage must be between 0 and 100 volts
- Percentage must be between 0 and 100
- Discharge rate must be positive
- Timestamp is optional (uses current time if not provided)

## Data Processing

### MAC Address Lookup
1. When submitting `/temperature` or `/powerstatus` data, the server looks up the MAC address in `external/sensors.json`
2. If the MAC address is found, the corresponding location is extracted and stored in the database
3. If the MAC address is not found, the location is stored as an empty string. You should update the database once you've added the location to the sensors.json file. Don't forget to call /reload-locations.

### Database Schema
The application creates tables matching this schema:
```sql
CREATE TABLE temp_humidity (
    location VARCHAR(64) NOT NULL,
    mac VARCHAR(64) NOT NULL,
    temperature NUMERIC NOT NULL,
    humidity NUMERIC NOT NULL,
    timestamp DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
    PRIMARY KEY (location, timestamp)
);

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

## Configuration

### Sensor Configuration (`external/sensors.json`)
Configure your sensors and their locations:
```json
{
    "sensors": {
        "temperature": [
            {
                "mac": "dd:cc:bb:aa:99:88",
                "location": "lounge"
            },
            {
                "mac": "aa:11:22:33:44:55",
                "location": "garage"
            }
        ],
        "air_quality": [
            {
                "mac": "22:ee:ff:aa:bb:cc",
                "location": "master bedroom"
            }
        ]
    }
}
```

**Important Notes:**
- MAC addresses must be in full 6-byte format: `xx:xx:xx:xx:xx:xx`
- You can reload the configuration without restarting the server by calling `/reload-locations`
- Sensors not in the configuration will have empty location values in the database

## Testing

### Python Test Script
Run the comprehensive test suite:
```bash
pipenv run python test_api.py
```

### cURL Test Script
Run tests using cURL commands:
```bash
./test_api.sh
```

### Manual Testing Examples

**Test connection:**
```bash
curl http://localhost:8000/connection
```

**Test temperature endpoint:**
```bash
curl -X POST http://localhost:8000/temperature \
  -H "Content-Type: application/json" \
  -d '{
    "mac": "dd:cc:bb:aa:99:88",
    "temperature": 23.2,
    "humidity": 50.6,
    "timestamp": "2024-07-18T02:44:22+00:00"
  }'
```

**Test power status endpoint:**
```bash
curl -X POST http://localhost:8000/powerstatus \
  -H "Content-Type: application/json" \
  -d '{
    "mac": "dd:cc:bb:aa:99:88",
    "voltage": 23.2,
    "percentage": 89.2,
    "dischargerate": 55,
    "timestamp": "2024-07-18T02:44:22+00:00"
  }'
```

**Test invalid MAC address (should fail):**
```bash
curl -X POST http://localhost:8000/temperature \
  -H "Content-Type: application/json" \
  -d '{
    "mac": "dd:cc",
    "temperature": 23.2,
    "humidity": 50.6
  }'
```


## Database Inspection
Query the database directly:
```bash
sqlite3 external/sensors.db "SELECT * FROM temp_humidity;"
sqlite3 external/sensors.db "SELECT * FROM nano_cell_battery;"
```

## Deployment

- Uvicorn: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Docker (see Dockerfile and compose.yml in parent directory)

## Error Handling

The server provides comprehensive error handling:
- **422 Unprocessable Entity**: Invalid input data (wrong types, invalid MAC format, out-of-range values)
- **500 Internal Server Error**: Database errors or unexpected server issues
- **Clear error messages**: Detailed validation error messages with field-specific information
