# Tap detection example.
# Will loop forever printing when a single or double click is detected.
# Open the serial port after running to see the output printed.
# Author: Tony DiCola
import board
import adafruit_lis3dh


# Uncomment _one_ of the hardware setups below depending on your wiring:

# Hardware I2C setup:
import busio
i2c = busio.I2C(board.SCL, board.SDA)
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19)

# Hardware I2C setup on CircuitPlayground Express:
# import busio
# i2c = busio.I2C(board.ACCELEROMETER_SCL, board.ACCELEROMETER_SDA)
# lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19)

# Software I2C setup:
#import bitbangio
#i2c = bitbangio.I2C(board.SCL, board.SDA)
#lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c)

# Hardware SPI setup:
#import busio
#spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
#cs = busio.DigitalInOut(board.D6)  # Set to appropriate CS pin!
#lis3dh = adafruit_lis3dh.LIS3DH_SPI(spi, cs)


# Set range of accelerometer (can be RANGE_2_G, RANGE_4_G, RANGE_8_G or RANGE_16_G).
lis3dh.range = adafruit_lis3dh.RANGE_2_G

# Set tap detection to double taps.  The first parameter is a value:
#  - 0 = Disable tap detection.
#  - 1 = Detect single taps.
#  - 2 = Detect double taps.
# The second parameter is the threshold and a higher value means less sensitive
# tap detection.  Note the threshold should be set based on the range above:
#  - 2G = 40-80 threshold
#  - 4G = 20-40 threshold
#  - 8G = 10-20 threshold
#  - 16G = 5-10 threshold
lis3dh.set_tap(2, 80)

# Loop forever printing if a double tap is detected. A single double tap may cause multiple
# `tapped` reads to return true so we make sure the last once was False.
last_tap = False
while True:
    tap = lis3dh.tapped
    if tap and not last_tap:
        print('Double tap!')
    last_tap = tap
