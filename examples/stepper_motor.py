# Run a Stepper Motor. Tested on ItsyBitsy M4 Express + DRV8833.
#   https://www.adafruit.com/product/3800
#   https://www.adafruit.com/product/3297

import time

import board
import pulseio
from adafruit_motor import stepper

AIn1 = pulseio.PWMOut(board.D9, frequency=1600)
AIn2 = pulseio.PWMOut(board.D10, frequency=1600)
BIn1 = pulseio.PWMOut(board.D11, frequency=1600)
BIn2 = pulseio.PWMOut(board.D12, frequency=1600)

stepper_motor = stepper.StepperMotor(AIn1, AIn2, BIn1, BIn2)

for i in range(1000):
    stepper_motor.onestep()
    time.sleep(0.01)

for i in range(1000):
    stepper_motor.onestep(direction=stepper.BACKWARD)
    time.sleep(0.01)
