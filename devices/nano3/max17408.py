from machine import SoftI2C, Pin # type: ignore

# Define I2C address and registers
MAX17048_ADDRESS = 0x36
MAX17048_VCELL = 0x02  # voltage register
MAX17048_SOC = 0x04  # percentage register
MAX17048_RATE = 0x16  # rate register

# Initialize I2C bus (adjust pins as needed)
i2c = SoftI2C(scl=Pin(3), sda=Pin(2))

class MAX1704:
    def __init__(self, i2c):
        self.i2c = i2c


    def read_register(self, reg):
        """Reads a 16-bit value from the specified register."""
        data = self.i2c.readfrom_mem(MAX17048_ADDRESS, reg, 2)
        return (data[0] << 8) | data[1]

    def get_voltage(self):
        voltage = (self.read_register(MAX17048_VCELL) * 78.125) / 1000000
        return voltage

    def get_percentage(self):
        # Read percentage
        percentage = self.read_register(MAX17048_SOC) / 256.0
        # The sensor can occasionally report > 100%, so we cap it.
        return min(percentage, 100.0)


    def get_dischargerate(self):
        # Read discharge rate in amps
        rate = (self.read_register(MAX17048_RATE) * 0.208) / 10000
        return rate

    def get_battery_info(self):
        # returns a tuple
        return (self.get_voltage(),
                self.get_percentage(),
                self.get_dischargerate())