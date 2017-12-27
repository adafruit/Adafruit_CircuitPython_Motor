import time

from board import *
import busio

# Import the PCA9685 module.
from adafruit_pca9685 import PCA9685

# This example also relies on the Adafruit motor library available here:
# https://github.com/adafruit/Adafruit_CircuitPython_Motor
from adafruit_motor import servo

i2c = busio.I2C(SCL, SDA)

# Create a simple PCA9685 class instance.
pca = PCA9685(i2c)
pca.frequency = 50

# The pulse range is 1000 - 2000 by default.
servo7 = servo.ContinuousServo(pca.channels[7], min_pulse=600, max_pulse=2500)

print("Forwards")
servo7.throttle = 1
time.sleep(1)

print("Backwards")
servo7.throttle = -1
time.sleep(1)

print("Stop")
servo7.throttle = 0

pca.deinit()
