# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import board
import pwmio
from adafruit_motor import servo

# create a PWMOut object on the control pin.
pwm = pwmio.PWMOut(board.D5, duty_cycle=0, frequency=50)

# The pulse range is 750 - 2250 by default, but this case assumes
# the servo may not use the standard 1-2 ms pulse width, so it
# will need to be calibrated.  For this we can set the limits
# to extremes
servo = servo.Servo(pwm, actuation_range=135, min_pulse=1, max_pulse=5000)

# This is where you would use different values for the pulse
# width and calculate the corresponding angle yourself

servo.pulse_width = 2000

# For this example, we'll assume that it was determined that
# 0 degrees is 1500 ms and 135 degrees is 2500 ms. This means
# you should initialize the servo.Servo object as follows:
#
# servo = servo.Servo(pwm, actuation_Range=135, min_pulse=1500, max_pulse=2500)
#
# You can now use the angle property as you normally would:
#
# servo.angle = 90 # Sets servo to 90 degrees
