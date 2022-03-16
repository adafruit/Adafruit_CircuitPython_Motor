# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

"""
`test_stepper`
====================================================

Tests stepper functionality.

* Author(s): ladyada
"""

__version__ = "1.0.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Motor.git"

import os
import sys
from unittest.mock import MagicMock

# Fix up the path to include our neighboring module.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
micropython = MagicMock()  # pylint: disable-msg=invalid-name
micropython.const = lambda x: x
sys.modules["micropython"] = micropython

from adafruit_motor import stepper  # pylint: disable-msg=wrong-import-position

# pylint: disable=consider-using-in


class Coil:
    """Class Coil"""

    def __init__(self):
        self._duty_cycle = 0

    @property
    def frequency(self):
        """Default frequency setting"""
        return 1500

    @property
    def duty_cycle(self):
        """16-bit duty cycle value"""
        return self._duty_cycle

    @duty_cycle.setter
    def duty_cycle(self, value):
        assert 0 <= value <= 0xFFFF
        self._duty_cycle = value


def test_single_coil():
    """Tests single coil"""
    coil = (Coil(), Coil(), Coil(), Coil())
    # We undo the coil order so our tests make more sense.
    motor = stepper.StepperMotor(coil[2], coil[0], coil[1], coil[3])
    # Always start with a single step.
    for j in range(4):
        assert coil[j].duty_cycle == (0xFFFF if j == 0 else 0)
    for i in range(1, 7):  # Test 6 steps so we wrap around
        motor.onestep()
        for j in range(4):
            assert coil[j].duty_cycle == (0xFFFF if i % 4 == j else 0)


def test_double_coil():
    """Tests double coil"""
    coil = (Coil(), Coil(), Coil(), Coil())
    # We undo the coil order so our tests make more sense.
    motor = stepper.StepperMotor(coil[2], coil[0], coil[1], coil[3])
    # Despite double stepping we always start with a single step.
    for j in range(4):
        assert coil[j].duty_cycle == (0xFFFF if j == 0 else 0)
    for i in range(6):  # Test 6 steps so we wrap around
        motor.onestep(style=stepper.DOUBLE)
        for j in range(4):
            assert coil[j].duty_cycle == (
                0xFFFF if i % 4 == j or (i + 1) % 4 == j else 0
            )


def test_interleave_steps():
    """Tests interleave steps"""
    coil = (Coil(), Coil(), Coil(), Coil())
    # We undo the coil order so our tests make more sense.
    motor = stepper.StepperMotor(coil[2], coil[0], coil[1], coil[3])
    # We always start with a single step.
    for j in range(4):
        assert coil[j].duty_cycle == (0xFFFF if j == 0 else 0)
    for i in range(15):  # Test 15 half steps so we wrap around
        motor.onestep(style=stepper.INTERLEAVE)
        for j in range(4):
            expected_value = 0
            # Even half steps should be DOUBLE coil active steps.
            if i % 2 == 0:
                if j == i // 2 % 4 or j == (i // 2 + 1) % 4:
                    expected_value = 0xFFFF
            # Odd half steps should be SINGLE coil active steps
            elif j == (i // 2 + 1) % 4:
                expected_value = 0xFFFF
            assert coil[j].duty_cycle == expected_value

    motor.onestep(direction=stepper.BACKWARD, style=stepper.INTERLEAVE)
    assert coil[0].duty_cycle == 0
    assert coil[1].duty_cycle == 0
    assert coil[2].duty_cycle == 0
    assert coil[3].duty_cycle == 0xFFFF


def test_microstep_steps():
    """Tests microsteps"""
    coil = (Coil(), Coil(), Coil(), Coil())
    # We undo the coil order so our tests make more sense.
    motor = stepper.StepperMotor(coil[2], coil[0], coil[1], coil[3], microsteps=2)
    # We always start with a single step.
    for j in range(4):
        assert coil[j].duty_cycle == (0xFFFF if j == 0 else 0)
    motor.onestep(style=stepper.MICROSTEP)
    assert coil[0].duty_cycle == 0xB504
    assert coil[1].duty_cycle == 0xB504
    assert coil[2].duty_cycle == 0
    assert coil[3].duty_cycle == 0

    motor.onestep(style=stepper.MICROSTEP)
    assert coil[0].duty_cycle == 0x0
    assert coil[1].duty_cycle == 0xFFFF
    assert coil[2].duty_cycle == 0
    assert coil[3].duty_cycle == 0

    motor.onestep(style=stepper.MICROSTEP)
    assert coil[0].duty_cycle == 0
    assert coil[1].duty_cycle == 0xB504
    assert coil[2].duty_cycle == 0xB504
    assert coil[3].duty_cycle == 0

    motor.onestep(direction=stepper.BACKWARD, style=stepper.MICROSTEP)
    assert coil[0].duty_cycle == 0x0
    assert coil[1].duty_cycle == 0xFFFF
    assert coil[2].duty_cycle == 0
    assert coil[3].duty_cycle == 0


def test_double_to_single():
    """Tests double to single movement"""
    coil = (Coil(), Coil(), Coil(), Coil())
    # We undo the coil order so our tests make more sense.
    motor = stepper.StepperMotor(coil[2], coil[0], coil[1], coil[3])
    # We always start with a single step.
    for j in range(4):
        assert coil[j].duty_cycle == (0xFFFF if j == 0 else 0)

    motor.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
    assert coil[0].duty_cycle == 0xFFFF
    assert coil[1].duty_cycle == 0
    assert coil[2].duty_cycle == 0
    assert coil[3].duty_cycle == 0xFFFF

    motor.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)
    assert coil[0].duty_cycle == 0
    assert coil[1].duty_cycle == 0
    assert coil[2].duty_cycle == 0
    assert coil[3].duty_cycle == 0xFFFF

    motor.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
    assert coil[0].duty_cycle == 0xFFFF
    assert coil[1].duty_cycle == 0
    assert coil[2].duty_cycle == 0
    assert coil[3].duty_cycle == 0xFFFF

    motor.onestep(direction=stepper.FORWARD, style=stepper.SINGLE)
    assert coil[0].duty_cycle == 0xFFFF
    assert coil[1].duty_cycle == 0
    assert coil[2].duty_cycle == 0
    assert coil[3].duty_cycle == 0


def test_microstep_to_single():
    """Tests microsteps to single movement"""
    coil = (Coil(), Coil(), Coil(), Coil())
    # We undo the coil order so our tests make more sense.
    motor = stepper.StepperMotor(coil[2], coil[0], coil[1], coil[3])
    # We always start with a single step.
    for j in range(4):
        assert coil[j].duty_cycle == (0xFFFF if j == 0 else 0)

    motor.onestep(direction=stepper.BACKWARD, style=stepper.MICROSTEP)
    assert coil[0].duty_cycle == 0xFEC3
    assert coil[1].duty_cycle == 0
    assert coil[2].duty_cycle == 0
    assert coil[3].duty_cycle == 0x1918

    motor.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)
    assert coil[0].duty_cycle == 0
    assert coil[1].duty_cycle == 0
    assert coil[2].duty_cycle == 0
    assert coil[3].duty_cycle == 0xFFFF

    motor.onestep(direction=stepper.FORWARD, style=stepper.MICROSTEP)
    assert coil[0].duty_cycle == 0x1918
    assert coil[1].duty_cycle == 0
    assert coil[2].duty_cycle == 0
    assert coil[3].duty_cycle == 0xFEC3

    motor.onestep(direction=stepper.FORWARD, style=stepper.SINGLE)
    assert coil[0].duty_cycle == 0xFFFF
    assert coil[1].duty_cycle == 0
    assert coil[2].duty_cycle == 0
    assert coil[3].duty_cycle == 0
