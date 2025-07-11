# sgp41.py - MicroPython driver for SGP41 VOC/NOx sensor with T/H compensation
import time
from micropython import const

class SGP41:
    """MicroPython driver for SGP41 VOC/NOx sensor with temperature/humidity compensation"""
    
    SGP41_I2C_ADDR = const(0x59)
    
    def __init__(self, i2c, address=SGP41_I2C_ADDR):
        self._i2c = i2c
        self._address = address
        self._initialized = False
        
    def detect(self):
        """Detect if SGP41 sensor is present on I2C bus"""
        try:
            devices = self._i2c.scan()
            return self._address in devices
        except Exception:
            return False
    
    def initialize(self):
        """Initialize the SGP41 sensor"""
        try:
            if not self.detect():
                return False
                
            # Reset sensor
            self._reset()
            time.sleep_ms(10)
            
            # Get serial number to verify communication
            serial = self._get_serial_number()
            if serial:
                self._initialized = True
                return True
            return False
        except Exception:
            return False
    
    def _reset(self):
        """Send soft reset command"""
        self._i2c.writeto(self._address, bytes([0x00, 0x06]))
        time.sleep_ms(50)
    
    def _get_serial_number(self):
        """Get sensor serial number"""
        try:
            self._i2c.writeto(self._address, bytes([0x36, 0x82]))
            time.sleep_ms(10)
            data = self._i2c.readfrom(self._address, 6)
            return data
        except Exception:
            return None
    
    def conditioning(self):
        """Run conditioning for 10 seconds (max)"""
        if not self._initialized:
            return None
            
        try:
            # SGP41 conditioning command
            self._i2c.writeto(self._address, bytes([0x26, 0x0F]))
            time.sleep_ms(30)
            
            # Read VOC raw value
            data = self._i2c.readfrom(self._address, 3)
            sraw_voc = (data[0] << 8) | data[1]
            return sraw_voc
        except Exception:
            return None
    
    def measure_raw(self, temperature=None, humidity=None):
        """
        Measure raw VOC and NOx values with optional temperature/humidity compensation
        
        Args:
            temperature: Temperature in degrees Celsius (optional, for compensation)
            humidity: Relative humidity in percent (optional, for compensation)
            
        Returns:
            Tuple of (sraw_voc, sraw_nox) or (None, None) if error
        """
        if not self._initialized:
            return None, None
            
        try:
            if temperature is not None and humidity is not None:
                # Use temperature and humidity compensation
                # Convert temperature and humidity to SGP41 format
                temp_ticks = self._convert_temperature(temperature)
                humidity_ticks = self._convert_humidity(humidity)
                
                # SGP41 measure raw with compensation command
                # Command: 0x26 0x0F + temperature + humidity
                cmd = bytearray([0x26, 0x0F, temp_ticks >> 8, temp_ticks & 0xFF, 
                               humidity_ticks >> 8, humidity_ticks & 0xFF])
                self._i2c.writeto(self._address, cmd)
            else:
                # Standard measurement without compensation
                self._i2c.writeto(self._address, bytes([0x26, 0x0F]))
            
            time.sleep_ms(30)
            
            # Read VOC and NOx raw values
            data = self._i2c.readfrom(self._address, 6)
            sraw_voc = (data[0] << 8) | data[1]
            sraw_nox = (data[3] << 8) | data[4]
            return sraw_voc, sraw_nox
        except Exception:
            return None, None
    
    def _convert_temperature(self, temperature):
        """Convert temperature to SGP41 ticks format"""
        # SGP41 temperature format: 16-bit signed integer
        # Temperature range: -45 to 130°C
        # Formula: ticks = (temperature + 45) * 65535 / 175
        ticks = int((temperature + 45) * 65535 / 175)
        return max(0, min(65535, ticks))
    
    def _convert_humidity(self, humidity):
        """Convert humidity to SGP41 ticks format"""
        # SGP41 humidity format: 16-bit unsigned integer
        # Humidity range: 0 to 100%
        # Formula: ticks = humidity * 65535 / 100
        ticks = int(humidity * 65535 / 100)
        return max(0, min(65535, ticks))
