"""
Utility functions for the sensors server.
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from decimal import Decimal

# Global cache for sensor configuration
_sensor_config_cache: Optional[Dict[str, Any]] = None

def load_sensor_config() -> Dict[str, Any]:
    """
    Load sensor configuration from external/sensors.json file.
    
    Returns:
        Dictionary containing sensor configuration
        
    Raises:
        FileNotFoundError: If sensors.json file doesn't exist
        json.JSONDecodeError: If sensors.json is invalid JSON
    """
    global _sensor_config_cache
    
    config_path = os.path.join("external", "sensors.json")
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Sensor configuration file not found: {config_path}")
    
    try:
        with open(config_path, 'r') as file:
            _sensor_config_cache = json.load(file)
        return _sensor_config_cache
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in sensors.json: {e}")

def get_sensor_config() -> Dict[str, Any]:
    """
    Get cached sensor configuration, loading it if not already cached.
    
    Returns:
        Dictionary containing sensor configuration
    """
    global _sensor_config_cache
    
    if _sensor_config_cache is None:
        _sensor_config_cache = load_sensor_config()
    
    return _sensor_config_cache

def reload_sensor_config() -> Dict[str, Any]:
    """
    Force reload of sensor configuration from file.
    
    Returns:
        Dictionary containing sensor configuration
    """
    global _sensor_config_cache
    _sensor_config_cache = None
    return load_sensor_config()

def get_location(sensor_type: str, mac_address: str) -> str:
    """
    Get location for a given MAC address and sensor type.
    
    Args:
        sensor_type: Type of sensor (e.g., 'temperature', 'air_quality')
        mac_address: MAC address to look up
        
    Returns:
        Location string if found, empty string if not found
    """
    try:
        config = get_sensor_config()
        sensors = config.get('sensors', {})
        sensor_list = sensors.get(sensor_type, [])
        
        # Find sensor with matching MAC address
        for sensor in sensor_list:
            if sensor.get('mac') == mac_address:
                return sensor.get('location', '')
        
        # MAC address not found
        return ''
        
    except Exception as e:
        print(f"Error looking up location for {mac_address}: {e=}")
        return ''

def convert_to_datetime(timestamp: str) -> datetime:
    """
    Convert ISO 8601 timestamp string to datetime object.
    
    Args:
        timestamp: ISO 8601 timestamp string
        
    Returns:
        datetime object with timezone information
        
    Raises:
        ValueError: If timestamp format is invalid
    """
    try:
        # Handle 'Z' timezone indicator
        if timestamp.endswith('Z'):
            timestamp = timestamp.replace('Z', '+00:00')
        
        return datetime.fromisoformat(timestamp)
    except ValueError as e:
        raise ValueError(f"Invalid timestamp format: {timestamp}") from e

def sanitize_input(value: Any) -> Any:
    """
    Sanitize input value to prevent injection attacks.
    
    Args:
        value: Input value to sanitize
        
    Returns:
        Sanitized value
    """
    if isinstance(value, str):
        # Remove any potentially dangerous characters
        return value.strip()
    return value

def convert_to_decimal(value: float) -> Decimal:
    """
    Convert float to Decimal for precise numeric storage.
    
    Args:
        value: Float value to convert
        
    Returns:
        Decimal value
    """
    return Decimal(str(value)) 