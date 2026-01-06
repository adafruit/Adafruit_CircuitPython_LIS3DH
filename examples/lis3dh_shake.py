# SPDX-FileCopyrightText: 2026 Carter Nelson for Adafruit Industries
# SPDX-License-Identifier: MIT

import time

import board
import busio

import adafruit_lis3dh

# Hardware I2C setup. Use the CircuitPlayground built-in accelerometer if available;
# otherwise check I2C pins.
if hasattr(board, "ACCELEROMETER_SCL"):
    i2c = busio.I2C(board.ACCELEROMETER_SCL, board.ACCELEROMETER_SDA)
    lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19)
else:
    i2c = board.I2C()  # uses board.SCL and board.SDA
    # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
    lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c)

# Hardware SPI setup:
# spi = board.SPI()
# cs = digitalio.DigitalInOut(board.D5)  # Set to correct CS pin!
# lis3dh = adafruit_lis3dh.LIS3DH_SPI(spi, cs)

# PyGamer or MatrixPortal I2C Setup:
# i2c = board.I2C()  # uses board.SCL and board.SDA
# lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19)

# Set range of accelerometer (can be RANGE_2_G, RANGE_4_G, RANGE_8_G or RANGE_16_G).
# Increase as needed depending on the expected magintude of shaking.
lis3dh.range = adafruit_lis3dh.RANGE_4_G

# OPTIONAL: Set threshold for shake, default is 20
# SHAKE_THRESH = 20

# Loop forever checking for shake
while True:
    # Check for shake
    if lis3dh.shake():
        print("SHAKE!!!")
    # Small delay to keep things responsive but give time for interrupt processing.
    time.sleep(0.1)
