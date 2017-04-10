# Click detection example.
# Will loop forever printing when a single or double click is detected.
# Open the serial port after running to see the output printed.
# Author: Tony DiCola
import time
import board
import adafruit_lis3dh


# Uncomment _one_ of the hardware setups below depending on your wiring:

# Hardware I2C setup:
import busio
i2c = busio.I2C(board.SCL, board.SDA)
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c)

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

# Set click detection to double and single clicks.  The first parameter is a value:
#  - 0 = Disable click detection.
#  - 1 = Detect single clicks.
#  - 2 = Detect single and double clicks.
# The second parameter is the threshold and a higher value means less sensitive
# click detection.  Note the threshold should be set based on the range above:
#  - 2G = 40-80 threshold
#  - 4G = 20-40 threshold
#  - 8G = 10-20 threshold
#  - 16G = 5-10 threshold
lis3dh.set_click(2, 80)

# Loop forever printing if a single or double click is detected.
while True:
    # Read the click detection.  Two booleans are returned, single click and
    # double click detected.  Each can be independently true/false.
    single, double = lis3dh.read_click()
    if single:
        print('Single click!')
    if double:
        print('Double click!')
    # Small delay to keep things responsive but give time for interrupt processing.
    time.sleep(0.05)
