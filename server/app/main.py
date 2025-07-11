"""
Main FastAPI application for the sensors server.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlmodel import Session
import logging

from .database import get_session, create_db_and_tables
from .schemas import TemperatureRequest, PowerStatusRequest, SGP41VOCRequest, ResponseMessage
from .services import process_temperature_data, process_power_status_data, process_sgp41_voc_data
from .utils import reload_sensor_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Sensors Server",
    description="FastAPI server for collecting sensor data",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Initialize database and load sensor configuration on startup."""
    try:
        create_db_and_tables()
        logger.info("Database tables created successfully")
        
        # Load sensor configuration
        reload_sensor_config()
        logger.info("Sensor configuration loaded successfully")
        
    except Exception as e:
        logger.error(f"Startup error: {e=}")
        raise

@app.get("/")
async def root():
    """Root endpoint returning 'Hello world'."""
    return PlainTextResponse("Hello world")

@app.get("/connection")
async def connection():
    """
    Simple connection test endpoint.
    Returns only a 200 status code.
    """
    return JSONResponse(status_code=status.HTTP_200_OK, content=None)

@app.get("/reload-locations", response_model=ResponseMessage)
async def reload_locations():
    """
    Reload sensor configuration from external/sensors.json file.
    """
    try:
        reload_sensor_config()
        logger.info("Sensor configuration reloaded successfully")
        return ResponseMessage(
            message="Sensor configuration reloaded successfully",
            status="success"
        )
    except Exception as e:
        logger.error(f"Error reloading sensor configuration: {e=}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reload sensor configuration: {str(e)}"
        )

@app.post("/temperature", status_code=status.HTTP_200_OK)
async def log_temperature(
    data: TemperatureRequest,
    session: Session = Depends(get_session)
):
    """
    Log temperature and humidity data from sensors.
    
    Accepts JSON with:
    - mac: MAC address of the sensor
    - temperature: Temperature reading
    - humidity: Humidity reading
    - timestamp: ISO 8601 timestamp (optional)
    """
    try:
        logger.info(f"Processing temperature data from {data.mac}")
        
        # Process and store the data
        process_temperature_data(session, data)
        
        logger.info(f"Successfully stored temperature data for {data.mac}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Temperature data stored successfully"}
        )
        
    except Exception as e:
        logger.error(f"Error processing temperature data: {e=}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process temperature data: {str(e)}"
        )

@app.post("/powerstatus", status_code=status.HTTP_200_OK)
async def log_power_status(
    data: PowerStatusRequest,
    session: Session = Depends(get_session)
):
    """
    Log power status data from sensors.
    
    Accepts JSON with:
    - mac: MAC address of the sensor
    - voltage: Battery voltage
    - percentage: Battery percentage
    - dischargerate: Discharge rate
    - timestamp: ISO 8601 timestamp (optional)
    """
    try:
        logger.info(f"Processing power status data from {data.mac}")
        
        # Process and store the data
        process_power_status_data(session, data)
        
        logger.info(f"Successfully stored power status data for {data.mac}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Power status data stored successfully"}
        )
        
    except Exception as e:
        logger.error(f"Error processing power status data: {e=}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process power status data: {str(e)}"
        )

@app.post("/sgp41-voc", status_code=status.HTTP_200_OK)
async def log_sgp41_voc(
    data: SGP41VOCRequest,
    session: Session = Depends(get_session)
):
    """
    Log SGP41 VOC and NOx data from sensors.
    
    Accepts JSON with:
    - mac: MAC address of the sensor
    - voc_raw: Raw VOC value from SGP41
    - nox_raw: Raw NOx value from SGP41
    - temperature: Temperature used for compensation
    - humidity: Humidity used for compensation
    - timestamp: ISO 8601 timestamp (optional)
    """
    try:
        logger.info(f"Processing SGP41 VOC data from {data.mac}")
        
        # Process and store the data
        process_sgp41_voc_data(session, data)
        
        logger.info(f"Successfully stored SGP41 VOC data for {data.mac}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "SGP41 VOC data stored successfully"}
        )
        
    except Exception as e:
        logger.error(f"Error processing SGP41 VOC data: {e=}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process SGP41 VOC data: {str(e)}"
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom exception handler for HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status": "error"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler for unexpected errors."""
    logger.error(f"Unexpected error: {exc=}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "status": "error"}
    ) 