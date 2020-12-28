import time

from board import SCL, SDA
import busio

# Import the PCA9685 module. Available in the bundle and here:
#   https://github.com/adafruit/Adafruit_CircuitPython_PCA9685
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

i2c = busio.I2C(SCL, SDA)

# Create a simple PCA9685 class instance.
pca = PCA9685(i2c)
# You can optionally provide a finer tuned reference clock speed to improve the accuracy of the
# timing pulses. This calibration will be specific to each board and its environment. See the
# calibration.py example in the PCA9685 driver.
# pca = PCA9685(i2c, reference_clock_speed=25630710)
pca.frequency = 50

# To get the full range of the servo you will likely need to adjust the min_pulse and max_pulse to
# match the stall points of the servo.
# This is an example for the Sub-micro servo: https://www.adafruit.com/product/2201
# servo7 = servo.Servo(pca.channels[7], min_pulse=580, max_pulse=2350)
# This is an example for the Micro Servo - High Powered, High Torque Metal Gear:
#   https://www.adafruit.com/product/2307
# servo7 = servo.Servo(pca.channels[7], min_pulse=500, max_pulse=2600)
# This is an example for the Standard servo - TowerPro SG-5010 - 5010:
#   https://www.adafruit.com/product/155
# servo7 = servo.Servo(pca.channels[7], min_pulse=400, max_pulse=2400)
# This is an example for the Analog Feedback Servo: https://www.adafruit.com/product/1404
# servo7 = servo.Servo(pca.channels[7], min_pulse=600, max_pulse=2500)
# This is an example for the Micro servo - TowerPro SG-92R: https://www.adafruit.com/product/169
# servo7 = servo.Servo(pca.channels[7], min_pulse=500, max_pulse=2400)

# The pulse range is 750 - 2250 by default. This range typically gives 135 degrees of
# range, but the default is to use 180 degrees. You can specify the expected range if you wish:
# servo7 = servo.Servo(pca.channels[7], actuation_range=135)
servo7 = servo.Servo(pca.channels[7])
servo7.trim = 50.0

# We sleep in the loops to give the servo time to move into position.
for i in range(0, 91):
    servo7.angle = i
    time.sleep(0.03)

for i in range(89, -91, -1):
    servo7.angle = i
    time.sleep(0.03)

for i in range(-89, 1, 1):
    servo7.angle = i
    time.sleep(0.03)


# You have to remember that the actuation range is a constant
# the trim simply sets where the perceived "0" angle is within that range

servo7.trim = 25.0
# you have a greater angle range on the + side with the trim set to 25.0
# and you will have a smaller ngle range on the - side
# -45...0...+135 = 180 total actuator range
#
# ** NOTE **
# Be sure in your application sode to set applicable limits to the trim based
# on how much of of the actuation range you will be using. If you need 90 degrees
# of actuator range (-45° to +45° with trim set to 50.0) and want to use the trim
# feature then you will need to use a servo that has 180 degrees of total range
# and set a minimum trim value of 25.0 and a maximum trim value of 75.0. This
# will keep any exceptions from being raised.

for i in range(0, 136):
    servo7.angle = i
    time.sleep(0.03)

for i in range(134, -46, -1):
    servo7.angle = i
    time.sleep(0.03)

for i in range(-44, 1, 1):
    servo7.angle = i
    time.sleep(0.03)

pca.deinit()
