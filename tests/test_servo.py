# SPDX-FileCopyrightText: 2026 Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

"""Tests for servo functionality."""

import pytest

from adafruit_motor.servo import ContinuousServo


class PWMOut:
    """Minimal PWM output used by servo tests."""

    def __init__(self) -> None:
        self.frequency = 50
        self.duty_cycle = 0


def test_continuous_servo_can_be_disabled_and_reenabled() -> None:
    """Setting throttle to None disables PWM and remains readable."""
    pwm = PWMOut()
    servo = ContinuousServo(pwm)

    servo.throttle = 0.5
    assert servo.throttle == pytest.approx(0.5, abs=0.001)

    servo.throttle = None
    assert pwm.duty_cycle == 0
    assert servo.throttle is None

    servo.throttle = -0.5
    assert servo.throttle == pytest.approx(-0.5, abs=0.001)
