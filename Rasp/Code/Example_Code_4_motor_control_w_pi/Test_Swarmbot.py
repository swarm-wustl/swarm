"""
L298N Motor Driver
"""

import RPi.GPIO as GPIO
import time
from argparse import ArgumentParser as Args

GPIO.setwarnings(True)

# Set up GPIO pins
GPIO.setmode(GPIO.BCM)

IN1 = 12
IN2 = 16
IN3 = 20
IN4 = 21

pins = [IN1, IN2, IN3, IN4]

for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)

# Set up PWM; left motor is half the speed of the right motor
pwm1 = GPIO.PWM(IN1, 100)
pwm2 = GPIO.PWM(IN3, 50)
pwm1.start(0)
pwm2.start(0)


# Main loop
while True:
    direction = input("Direction (f, b, l, r): ")
    if direction == 'f':
        GPIO.output(IN1, 1)
        GPIO.output(IN2, 0)
        GPIO.output(IN3, 1)
        GPIO.output(IN4, 0)
    elif direction == 'b':
        GPIO.output(IN1, 0)
        GPIO.output(IN2, 1)
        GPIO.output(IN3, 0)
        GPIO.output(IN4, 1)
    elif direction == 'l':
        GPIO.output(IN1, 0)
        GPIO.output(IN2, 1)
        GPIO.output(IN3, 1)
        GPIO.output(IN4, 0)
    elif direction == 'r':
        GPIO.output(IN1, 1)
        GPIO.output(IN2, 0)
        GPIO.output(IN3, 0)
        GPIO.output(IN4, 1)
    else:
        break

