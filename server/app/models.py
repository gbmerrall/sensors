"""
Database models for the sensors server using SQLModel.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from decimal import Decimal

class TempHumidity(SQLModel, table=True):
    """Temperature and humidity sensor data model."""
    __tablename__ = "temp_humidity"
    
    location: str = Field(max_length=64, primary_key=True)
    mac: str = Field(max_length=64)
    temperature: Decimal = Field(max_digits=10, decimal_places=2)
    humidity: Decimal = Field(max_digits=10, decimal_places=2)
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        primary_key=True,
        sa_column_kwargs={"server_default": "CURRENT_TIMESTAMP"}
    )

class NanoCellBattery(SQLModel, table=True):
    """Nano cell battery status data model."""
    __tablename__ = "nano_cell_battery"
    
    location: str = Field(max_length=64, primary_key=True)
    mac: str = Field(max_length=64)
    voltage: Decimal = Field(max_digits=10, decimal_places=2)
    percentage: Decimal = Field(max_digits=10, decimal_places=2)
    dischargerate: Decimal = Field(max_digits=10, decimal_places=2)
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        primary_key=True,
        sa_column_kwargs={"server_default": "CURRENT_TIMESTAMP"}
    )

class SGP41VOCData(SQLModel, table=True):
    """SGP41 VOC and NOx sensor data model."""
    __tablename__ = "sgp41_voc_data"
    
    location: str = Field(max_length=64, primary_key=True)
    mac: str = Field(max_length=64)
    voc_raw: int = Field(description="Raw VOC value from SGP41")
    nox_raw: int = Field(description="Raw NOx value from SGP41")
    temperature: Decimal = Field(max_digits=10, decimal_places=2, description="Temperature used for compensation")
    humidity: Decimal = Field(max_digits=10, decimal_places=2, description="Humidity used for compensation")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        primary_key=True,
        sa_column_kwargs={"server_default": "CURRENT_TIMESTAMP"}
    ) 