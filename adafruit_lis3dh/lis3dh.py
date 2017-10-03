# Adafruit LIS3DH Accelerometer CircuitPython Driver
# Based on the Arduino LIS3DH driver from:
#   https://github.com/adafruit/Adafruit_LIS3DH/
# Author: Tony DiCola
# License: MIT License (https://en.wikipedia.org/wiki/MIT_License)
try:
    import struct
except ImportError:
    import ustruct as struct

from micropython import const

# Register addresses:
REG_OUTADC1_L   = const(0x08)
REG_WHOAMI      = const(0x0F)
REG_TEMPCFG     = const(0x1F)
REG_CTRL1       = const(0x20)
REG_CTRL3       = const(0x22)
REG_CTRL4       = const(0x23)
REG_CTRL5       = const(0x24)
REG_OUT_X_L     = const(0x28)
REG_CLICKCFG    = const(0x38)
REG_CLICKSRC    = const(0x39)
REG_CLICKTHS    = const(0x3A)
REG_TIMELIMIT   = const(0x3B)
REG_TIMELATENCY = const(0x3C)
REG_TIMEWINDOW  = const(0x3D)

# Register value constants:
RANGE_16_G               = const(0b11)    # +/- 16g
RANGE_8_G                = const(0b10)    # +/- 8g
RANGE_4_G                = const(0b01)    # +/- 4g
RANGE_2_G                = const(0b00)    # +/- 2g (default value)
DATARATE_400_HZ          = const(0b0111)  # 400Hz
DATARATE_200_HZ          = const(0b0110)  # 200Hz
DATARATE_100_HZ          = const(0b0101)  # 100Hz
DATARATE_50_HZ           = const(0b0100)  # 50Hz
DATARATE_25_HZ           = const(0b0011)  # 25Hz
DATARATE_10_HZ           = const(0b0010)  # 10 Hz
DATARATE_1_HZ            = const(0b0001)  # 1 Hz
DATARATE_POWERDOWN       = const(0)
DATARATE_LOWPOWER_1K6HZ  = const(0b1000)
DATARATE_LOWPOWER_5KHZ   = const(0b1001)


class LIS3DH:

    def __init__(self):
        # Check device ID.
        device_id = self._read_register_byte(REG_WHOAMI)
        if device_id != 0x33:
            raise RuntimeError('Failed to find LIS3DH!')
        # Enable all axes, normal mode.
        self._write_register_byte(REG_CTRL1, 0x07)
        # Set 400Hz data rate.
        self.data_rate = DATARATE_400_HZ
        # High res & BDU enabled.
        self._write_register_byte(REG_CTRL4, 0x88)
        # DRDY on INT1.
        self._write_register_byte(REG_CTRL3, 0x10)
        # Enable ADCs.
        self._write_register_byte(REG_TEMPCFG, 0x80)

    @property
    def data_rate(self):
        """Get/set the data rate of the accelerometer.  Can be DATA_RATE_400_HZ,
        DATA_RATE_200_HZ, DATA_RATE_100_HZ, DATA_RATE_50_HZ, DATA_RATE_25_HZ,
        DATA_RATE_10_HZ, DATA_RATE_1_HZ, DATA_RATE_POWERDOWN, DATA_RATE_LOWPOWER_1K6HZ,
        or DATA_RATE_LOWPOWER_5KHZ.
        """
        ctl1 = self._read_register_byte(REG_CTRL1)
        return (ctl1 >> 4) & 0x0F

    @data_rate.setter
    def data_rate(self, rate):
        ctl1 = self._read_register_byte(REG_CTRL1)
        ctl1 &= ~(0xF0)
        ctl1 |= rate << 4
        self._write_register_byte(REG_CTRL1, ctl1)

    @property
    def range(self):
        """Get/set the range of the accelerometer.  Can be RANGE_2_G, RANGE_4_G,
        RANGE_8_G, or RANGE_16_G.
        """
        ctl4 = self._read_register_byte(REG_CTRL4)
        return (ctl4 >> 4) & 0x03

    @range.setter
    def range(self, range_value):
        ctl4 = self._read_register_byte(REG_CTRL4)
        ctl4 &= ~(0x30)
        ctl4 |= range_value << 4
        self._write_register_byte(REG_CTRL4, ctl4)

    @property
    def acceleration(self):
        """Read the x, y, z acceleration values.  These values are returned in
        a 3-tuple and are in m / s ^ 2.
        """
        data = self._read_register(REG_OUT_X_L | 0x80, 6)
        x = struct.unpack('<h', data[0:2])[0]
        y = struct.unpack('<h', data[2:4])[0]
        z = struct.unpack('<h', data[4:6])[0]
        divider = 1
        accel_range = self.range
        if accel_range == RANGE_16_G:
            divider = 1365
        elif accel_range == RANGE_8_G:
            divider = 4096
        elif accel_range == RANGE_4_G:
            divider = 8190
        elif accel_range == RANGE_2_G:
            divider = 16380
        return (x / divider * 9.806, y / divider * 9.806, z / divider * 9.806)

    def read_adc_raw(self, adc):
        """Retrieve the raw analog to digital converter value.  ADC must be a
        value 1, 2, or 3.
        """
        if adc < 1 or adc > 3:
            raise ValueError('ADC must be a value 1 to 3!')
        data = self._read_register((REG_OUTADC1_L+((adc-1)*2)) | 0x80, 2)
        return struct.unpack('<h', data[0:2])[0]

    def read_adc_mV(self, adc):
        """Read the specified analog to digital converter value in millivolts.
        ADC must be a value 1, 2, or 3.  NOTE the ADC can only measure voltages
        in the range of ~900-1200mV!
        """
        raw = self.read_adc_raw(adc)
        # Interpolate between 900mV and 1800mV, see:
        # https://learn.adafruit.com/adafruit-lis3dh-triple-axis-accelerometer-breakout/wiring-and-test#reading-the-3-adc-pins
        # This is a simplified linear interpolation of:
        # return y0 + (x-x0)*((y1-y0)/(x1-x0))
        # Where:
        #   x = ADC value
        #   x0 = -32512
        #   x1 = 32512
        #   y0 = 1800
        #   y1 = 900
        return 1800+(raw+32512)*(-900/65024)

    def read_click_raw(self):
        """Read the raw click register byte value."""
        return self._read_register_byte(REG_CLICKSRC)

    def read_click(self):
        """Read a 2-tuple of bools where the first value is True if a single
        click was detected and the second value is True if a double click was
        detected.
        """
        raw = self.read_click_raw()
        return (raw & 0x10 > 0, raw & 0x20 > 0)

    def set_click(self, click, threshold, time_limit=10, time_latency=20, time_window=255, click_cfg=None):
        """Set the click detection parameters.  Must specify at least:
            click - Set to 0 to disable click detection, 1 to detect only single
                    clicks, and 2 to detect single & double clicks.
            threshold - A threshold for the click detection.  The higher the value
                        the less sensitive the detection.  This changes based on
                        the accelerometer range.  Good values are 5-10 for 16G,
                        10-20 for 8G, 20-40 for 4G, and 40-80 for 2G.
          Optionally specify (see datasheet for meaning of these):
            time_limit - Time limit register value (default 10).
            time_latency - Time latency register value (default 20).
            time_window - Time window register value (default 255).
        """
        if (click < 0 or click > 2) and click_cfg is None:
            raise ValueError('Click must be 0 (disabled), 1 (single click), or 2 (double click)!')
        if click == 0 and click_cfg is None:
            # Disable click interrupt.
            r = self._read_register_byte(REG_CTRL3)
            r &= ~(0x80)  # Turn off I1_CLICK.
            self._write_register_byte(REG_CTRL3, r)
            self._write_register_byte(REG_CLICKCFG, 0)
            return
        # Else enable click with specified parameters.
        self._write_register_byte(REG_CTRL3, 0x80)  # Turn on int1 click.
        self._write_register_byte(REG_CTRL5, 0x08)  # Latch interrupt on int1.
        if click_cfg is not None:
            # Custom click configuration register value specified, use it.
            self._write_register_byte(REG_CLICKCFG, click_cfg)
        elif click == 1:
            self._write_register_byte(REG_CLICKCFG, 0x15)  # Turn on all axes & singletap.
        elif click == 2:
            self._write_register_byte(REG_CLICKCFG, 0x2A)  # Turn on all axes & doubletap.
        self._write_register_byte(REG_CLICKTHS, threshold)
        self._write_register_byte(REG_TIMELIMIT, time_limit)
        self._write_register_byte(REG_TIMELATENCY, time_latency)
        self._write_register_byte(REG_TIMEWINDOW, time_window)

    def _read_register_byte(self, register):
        # Read a byte register value and return it.
        return self._read_register(register, 1)[0]

    def _read_register(self, register, length):
        # Read an arbitrarily long register (specified by length number of
        # bytes) and return a bytearray of the retrieved data.
        # Subclasses MUST implement this!
        raise NotImplementedError

    def _write_register_byte(self, register, value):
        # Write a single byte register at the specified register address.
        # Subclasses MUST implement this!
        raise NotImplementedError


class LIS3DH_I2C(LIS3DH):

    def __init__(self, i2c, address=0x18):
        import adafruit_bus_device.i2c_device as i2c_device
        self._i2c = i2c_device.I2CDevice(i2c, address)
        self._buffer = bytearray(6)
        super().__init__()

    def _read_register(self, register, length):
        self._buffer[0] = register & 0xFF
        with self._i2c as i2c:
            i2c.write(self._buffer, start=0, end=1)
            i2c.read_into(self._buffer, start=0, end=length)
            return self._buffer

    def _write_register_byte(self, register, value):
        self._buffer[0] = register & 0xFF
        self._buffer[1] = value & 0xFF
        with self._i2c as i2c:
            i2c.write(self._buffer, start=0, end=2)


class LIS3DH_SPI(LIS3DH):

    def __init__(self, spi, cs, baudrate=100000):
        import adafruit_bus_device.spi_device as spi_device
        self._spi = spi_device.SPIDevice(spi, cs, baudrate=baudrate)
        self._buffer = bytearray(6)
        super().__init__()

    def _read_register(self, register, length):
        if length == 1:
            self._buffer[0] = (register | 0x80) & 0xFF  # Read single, bit 7 high.
        else:
            self._buffer[0] = (register | 0xC0) & 0xFF  # Read multiple, bit 6&7 high.
        with self._spi as spi:
            spi.write(self._buffer, start=0, end=1)
            spi.readinto(self._buffer, start=0, end=length)
            return self._buffer

    def _write_register_byte(self, register, value):
        self._buffer[0] = (register & (~0x80 & 0xFF)) & 0xFF  # Write, bit 7 low.
        self._buffer[1] = value & 0xFF
        with self._spi as spi:
            spi.write(self._buffer, start=0, end=2)
