"""
Service layer for business logic and database operations.
"""
from sqlmodel import Session, select
from datetime import datetime

from .models import TempHumidity, NanoCellBattery
from .schemas import TemperatureRequest, PowerStatusRequest
from .utils import get_location, convert_to_datetime, convert_to_decimal, sanitize_input

def process_temperature_data(
    session: Session, 
    data: TemperatureRequest
) -> TempHumidity:
    """
    Process and store temperature/humidity data.
    
    Args:
        session: Database session
        data: Validated temperature request data
        
    Returns:
        Created TempHumidity record
        
    Raises:
        Exception: If database operation fails
    """
    try:
        # Sanitize inputs
        mac = sanitize_input(data.mac)
        temperature = convert_to_decimal(data.temperature)
        humidity = convert_to_decimal(data.humidity)
        
        # Get location from sensor configuration
        location = get_location('temperature', mac)
        
        # Handle timestamp
        if data.timestamp:
            timestamp = convert_to_datetime(data.timestamp)
        else:
            timestamp = datetime.utcnow()
        
        # Create database record
        temp_humidity = TempHumidity(
            location=location,
            mac=mac,
            temperature=temperature,
            humidity=humidity,
            timestamp=timestamp
        )
        
        # Add to database
        session.add(temp_humidity)
        session.commit()
        session.refresh(temp_humidity)
        
        print(f"Added temperature data: {mac=}, {temperature=}, {humidity=}, {location=}")
        
        return temp_humidity
        
    except Exception as e:
        session.rollback()
        print(f"Error processing temperature data: {e=}")
        raise

def process_power_status_data(
    session: Session, 
    data: PowerStatusRequest
) -> NanoCellBattery:
    """
    Process and store power status data.
    
    Args:
        session: Database session
        data: Validated power status request data
        
    Returns:
        Created NanoCellBattery record
        
    Raises:
        Exception: If database operation fails
    """
    try:
        # Sanitize inputs
        mac = sanitize_input(data.mac)
        voltage = convert_to_decimal(data.voltage)
        percentage = convert_to_decimal(data.percentage)
        dischargerate = convert_to_decimal(data.dischargerate)
        
        # Get location from sensor configuration
        # Note: Power status might be from different sensor types, 
        # so we'll check multiple types or use empty string if not found
        location = get_location('temperature', mac)  # Check temperature sensors first
        if not location:
            # Could extend to check other sensor types if needed
            location = ''
        
        # Handle timestamp
        if data.timestamp:
            timestamp = convert_to_datetime(data.timestamp)
        else:
            timestamp = datetime.utcnow()
        
        # Create database record
        battery_status = NanoCellBattery(
            location=location,
            mac=mac,
            voltage=voltage,
            percentage=percentage,
            dischargerate=dischargerate,
            timestamp=timestamp
        )
        
        # Add to database
        session.add(battery_status)
        session.commit()
        session.refresh(battery_status)
        
        print(f"Added power status data: {mac=}, {voltage=}, {percentage=}, {dischargerate=}, {location=}")
        
        return battery_status
        
    except Exception as e:
        session.rollback()
        print(f"Error processing power status data: {e=}")
        raise

def get_recent_temperature_data(
    session: Session, 
    limit: int = 10
) -> list[TempHumidity]:
    """
    Get recent temperature/humidity data.
    
    Args:
        session: Database session
        limit: Maximum number of records to return
        
    Returns:
        List of recent temperature/humidity records
    """
    statement = select(TempHumidity).order_by(TempHumidity.timestamp.desc()).limit(limit)
    return session.exec(statement).all()

def get_recent_power_status_data(
    session: Session, 
    limit: int = 10
) -> list[NanoCellBattery]:
    """
    Get recent power status data.
    
    Args:
        session: Database session
        limit: Maximum number of records to return
        
    Returns:
        List of recent power status records
    """
    statement = select(NanoCellBattery).order_by(NanoCellBattery.timestamp.desc()).limit(limit)
    return session.exec(statement).all() 