"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
import re

class TemperatureRequest(BaseModel):
    """Request schema for temperature/humidity data."""
    mac: str = Field(..., description="MAC address of the sensor")
    temperature: float = Field(..., description="Temperature reading")
    humidity: float = Field(..., description="Humidity reading")
    timestamp: Optional[str] = Field(None, description="ISO 8601 timestamp with timezone")
    
    @validator('mac')
    def validate_mac_address(cls, v):
        """Validate MAC address format."""
        # MAC address pattern: xx:xx:xx:xx:xx:xx (full 6-byte format)
        mac_pattern = r'^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$'
        if not re.match(mac_pattern, v):
            raise ValueError('Invalid MAC address format. Expected format: xx:xx:xx:xx:xx:xx')
        return v
    
    @validator('temperature')
    def validate_temperature(cls, v):
        """Validate temperature is a reasonable value."""
        if not isinstance(v, (int, float)):
            raise ValueError('Temperature must be a number')
        if v < -50 or v > 100:
            raise ValueError('Temperature must be between -50 and 100 degrees')
        return float(v)
    
    @validator('humidity')
    def validate_humidity(cls, v):
        """Validate humidity is a reasonable value."""
        if not isinstance(v, (int, float)):
            raise ValueError('Humidity must be a number')
        if v < 0 or v > 100:
            raise ValueError('Humidity must be between 0 and 100 percent')
        return float(v)
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """Validate timestamp format."""
        if v is None:
            return v
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError('Invalid timestamp format. Expected ISO 8601 format')

class PowerStatusRequest(BaseModel):
    """Request schema for power status data."""
    mac: str = Field(..., description="MAC address of the sensor")
    voltage: float = Field(..., description="Battery voltage")
    percentage: float = Field(..., description="Battery percentage")
    dischargerate: float = Field(..., description="Discharge rate")
    timestamp: Optional[str] = Field(None, description="ISO 8601 timestamp with timezone")
    
    @validator('mac')
    def validate_mac_address(cls, v):
        """Validate MAC address format."""
        mac_pattern = r'^([0-9A-Fa-f]{2}[:-]){1,5}([0-9A-Fa-f]{2})$'
        if not re.match(mac_pattern, v):
            raise ValueError('Invalid MAC address format. Expected format: xx:xx or xx:xx:xx:xx:xx:xx')
        return v
    
    @validator('voltage')
    def validate_voltage(cls, v):
        """Validate voltage is a reasonable value."""
        if not isinstance(v, (int, float)):
            raise ValueError('Voltage must be a number')
        if v < 0 or v > 100:
            raise ValueError('Voltage must be between 0 and 100 volts')
        return float(v)
    
    @validator('percentage')
    def validate_percentage(cls, v):
        """Validate percentage is a reasonable value."""
        if not isinstance(v, (int, float)):
            raise ValueError('Percentage must be a number')
        if v < 0 or v > 100:
            raise ValueError('Percentage must be between 0 and 100')
        return float(v)
    
    @validator('dischargerate')
    def validate_dischargerate(cls, v):
        """Validate discharge rate is a reasonable value."""
        if not isinstance(v, (int, float)):
            raise ValueError('Discharge rate must be a number')
        if v < 0:
            raise ValueError('Discharge rate must be positive')
        return float(v)
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """Validate timestamp format."""
        if v is None:
            return v
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError('Invalid timestamp format. Expected ISO 8601 format')

class ResponseMessage(BaseModel):
    """Generic response message."""
    message: str
    status: str = "success" 

class SGP41VOCRequest(BaseModel):
    """Request schema for SGP41 VOC/NOx data."""
    mac: str = Field(..., description="MAC address of the sensor")
    voc_raw: int = Field(..., description="Raw VOC value from SGP41")
    nox_raw: int = Field(..., description="Raw NOx value from SGP41")
    temperature: float = Field(..., description="Temperature used for compensation")
    humidity: float = Field(..., description="Humidity used for compensation")
    timestamp: Optional[str] = Field(None, description="ISO 8601 timestamp with timezone")
    
    @validator('mac')
    def validate_mac_address(cls, v):
        """Validate MAC address format."""
        # MAC address pattern: xx:xx:xx:xx:xx:xx (full 6-byte format)
        mac_pattern = r'^([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]{2})$'
        if not re.match(mac_pattern, v):
            raise ValueError('Invalid MAC address format. Expected format: xx:xx:xx:xx:xx:xx')
        return v
    
    @validator('voc_raw')
    def validate_voc_raw(cls, v):
        """Validate VOC raw value."""
        if not isinstance(v, int):
            raise ValueError('VOC raw value must be an integer')
        if v < 0:
            raise ValueError('VOC raw value must be non-negative')
        return v
    
    @validator('nox_raw')
    def validate_nox_raw(cls, v):
        """Validate NOx raw value."""
        if not isinstance(v, int):
            raise ValueError('NOx raw value must be an integer')
        if v < 0:
            raise ValueError('NOx raw value must be non-negative')
        return v
    
    @validator('temperature')
    def validate_temperature(cls, v):
        """Validate temperature is a reasonable value."""
        if not isinstance(v, (int, float)):
            raise ValueError('Temperature must be a number')
        if v < -50 or v > 100:
            raise ValueError('Temperature must be between -50 and 100 degrees')
        return float(v)
    
    @validator('humidity')
    def validate_humidity(cls, v):
        """Validate humidity is a reasonable value."""
        if not isinstance(v, (int, float)):
            raise ValueError('Humidity must be a number')
        if v < 0 or v > 100:
            raise ValueError('Humidity must be between 0 and 100 percent')
        return float(v)
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """Validate timestamp format."""
        if v is None:
            return v
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except ValueError:
            raise ValueError('Invalid timestamp format. Expected ISO 8601 format') 