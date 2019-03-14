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
`adafruit_motor.stepper`
====================================================

Stepper motors feature multiple wire coils that are used to rotate the magnets connected to the
motor shaft in a precise way. Each increment of the motor is called a step. Stepper motors have a
varying number of steps per rotation so check the motor's documentation to determine exactly how
precise each step is.

* Author(s): Tony DiCola, Scott Shawcroft
"""

import math

from micropython import const

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Motor.git"

# Stepper Motor Shield/Wing Driver
# Based on Adafruit Motorshield library:
# https://github.com/adafruit/Adafruit_Motor_Shield_V2_Library

# Constants that specify the direction and style of steps.
FORWARD = const(1)
"""Step forward"""
BACKWARD = const(2)
""""Step backward"""
SINGLE = const(1)
"""Step so that each step only activates a single coil"""
DOUBLE = const(2)
"""Step so that each step only activates two coils to produce more torque."""
INTERLEAVE = const(3)
"""Step half a step to alternate between single coil and double coil steps."""
MICROSTEP = const(4)
"""Step a fraction of a step by partially activating two neighboring coils. Step size is determined
   by ``microsteps`` constructor argument."""

class StepperMotor:
    """A bipolar stepper motor or four coil unipolar motor.

    :param ~pulseio.PWMOut ain1: `pulseio.PWMOut`-compatible output connected to the driver for
      the first coil (unipolar) or first input to first coil (bipolar).
    :param ~pulseio.PWMOut ain2: `pulseio.PWMOut`-compatible output connected to the driver for
      the third coil (unipolar) or second input to first coil (bipolar).
    :param ~pulseio.PWMOut bin1: `pulseio.PWMOut`-compatible output connected to the driver for
      the second coil (unipolar) or second input to second coil (bipolar).
    :param ~pulseio.PWMOut bin2: `pulseio.PWMOut`-compatible output connected to the driver for
      the fourth coil (unipolar) or second input to second coil (bipolar).
    :param int microsteps: Number of microsteps between full steps. Must be at least 2 and even.
    """
    def __init__(self, ain1, ain2, bin1, bin2, *, microsteps=16):
        self._coil = (ain2, bin1, ain1, bin2)

	# set a safe pwm freq for each output
        for i in range(4):
            if self._coil[i].frequency < 1500:
                self._coil[i].frequency = 2000

        self._current_microstep = 0
        if microsteps < 2:
            raise ValueError("Microsteps must be at least 2")
        if microsteps % 2 == 1:
            raise ValueError("Microsteps must be even")
        self._microsteps = microsteps
        self._curve = [int(round(0xffff * math.sin(math.pi / (2 * microsteps) * i)))
                       for i in range(microsteps + 1)]
        self._update_coils()

    def _update_coils(self, *, microstepping=False):
        duty_cycles = [0, 0, 0, 0]
        trailing_coil = (self._current_microstep // self._microsteps) % 4
        leading_coil = (trailing_coil + 1) % 4
        microstep = self._current_microstep % self._microsteps
        duty_cycles[leading_coil] = self._curve[microstep]
        duty_cycles[trailing_coil] = self._curve[self._microsteps - microstep]

        # This ensures DOUBLE steps use full torque. Without it, we'd use partial torque from the
        # microstepping curve (0xb504).
        if not microstepping and (duty_cycles[leading_coil] == duty_cycles[trailing_coil] and
                                  duty_cycles[leading_coil] > 0):
            duty_cycles[leading_coil] = 0xffff
            duty_cycles[trailing_coil] = 0xffff

        # Energize coils as appropriate:
        for i in range(4):
            self._coil[i].duty_cycle = duty_cycles[i]

    def release(self):
        """Releases all the coils so the motor can free spin, also won't use any power"""
        # De-energize coils:
        for i in range(4):
            self._coil[i].duty_cycle = 0

    def onestep(self, *, direction=FORWARD, style=SINGLE):
        """Performs one step of a particular style. The actual rotation amount will vary by style.
           `SINGLE` and `DOUBLE` will normal cause a full step rotation. `INTERLEAVE` will normally
           do a half step rotation. `MICROSTEP` will perform the smallest configured step.

           When step styles are mixed, subsequent `SINGLE`, `DOUBLE` or `INTERLEAVE` steps may be
           less than normal in order to align to the desired style's pattern.

           :param int direction: Either `FORWARD` or `BACKWARD`
           :param int style: `SINGLE`, `DOUBLE`, `INTERLEAVE`"""
        # Adjust current steps based on the direction and type of step.
        step_size = 0
        if style == MICROSTEP:
            step_size = 1
        else:
            half_step = self._microsteps // 2
            full_step = self._microsteps
            # Its possible the previous steps were MICROSTEPS so first align with the interleave
            # pattern.
            additional_microsteps = self._current_microstep % half_step
            if additional_microsteps != 0:
                # We set _current_microstep directly because our step size varies depending on the
                # direction.
                if direction == FORWARD:
                    self._current_microstep += half_step - additional_microsteps
                else:
                    self._current_microstep -= additional_microsteps
                step_size = 0
            elif style == INTERLEAVE:
                step_size = half_step

            current_interleave = self._current_microstep // half_step
            if ((style == SINGLE and current_interleave % 2 == 1) or
                    (style == DOUBLE and current_interleave % 2 == 0)):
                step_size = half_step
            elif style in (SINGLE, DOUBLE):
                step_size = full_step

        if direction == FORWARD:
            self._current_microstep += step_size
        else:
            self._current_microstep -= step_size

        # Now that we know our target microstep we can determine how to energize the four coils.
        self._update_coils(microstepping=style == MICROSTEP)

        return self._current_microstep
