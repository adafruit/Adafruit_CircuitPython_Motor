# The MIT License (MIT)
#
# Copyright (c) 2017 Scott Shawcroft for Adafruit Industries LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_motor.motor`
====================================================

Simple control of a DC motor. DC motors have two wires and should not be connected directly to
the PWM connections. Instead use intermediate circuitry to control a much stronger power source with
the PWM. The `Adafruit Stepper + DC Motor FeatherWing <https://www.adafruit.com/product/2927>`_,
`Adafruit TB6612 1.2A DC/Stepper Motor Driver Breakout Board
<https://www.adafruit.com/product/2448>`_ and `Adafruit Motor/Stepper/Servo Shield for Arduino v2
Kit - v2.3 <https://www.adafruit.com/product/1438>`_ do this for popular form
factors already.

.. note:: The TB6612 boards feature three inputs XIN1, XIN2 and PWMX. Since we PWM the INs directly
  its expected that the PWM pin is consistently high.

* Author(s): Scott Shawcroft
"""

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Motor.git"

class DCMotor:
    """DC motor driver. ``positive_pwm`` and ``negative_pwm`` can be swapped if the motor runs in
       the opposite direction from what was expected for "forwards".

       :param ~pulseio.PWMOut positive_pwm: The motor input that causes the motor to spin forwards
         when high and the other is low.
       :param ~pulseio.PWMOut negative_pwm: The motor input that causes the motor to spin backwards
         when high and the other is low."""
    def __init__(self, positive_pwm, negative_pwm):
        self._positive = positive_pwm
        self._negative = negative_pwm
        self._throttle = None

    @property
    def throttle(self):
        """Motor speed, ranging from -1.0 (full speed reverse) to 1.0 (full speed forward),
        or ``None``.
        If ``None``, both PWMs are turned full off. If ``0.0``, both PWMs are turned full on.
        """
        return self._throttle

    @throttle.setter
    def throttle(self, value):
        if value is not None and (value > 1.0 or value < -1.0):
            raise ValueError("Throttle must be None or between -1.0 and 1.0")
        self._throttle = value
        if value is None:
            self._positive.duty_cycle = 0
            self._negative.duty_cycle = 0
        elif value == 0:
            self._positive.duty_cycle = 0xffff
            self._negative.duty_cycle = 0xffff
        else:
            duty_cycle = int(0xffff * abs(value))
            if value < 0:
                self._positive.duty_cycle = 0
                self._negative.duty_cycle = duty_cycle
            else:
                self._positive.duty_cycle = duty_cycle
                self._negative.duty_cycle = 0

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.throttle = None

    def deinit(self):
        """Stop using the motor."""
        self.throttle = None
