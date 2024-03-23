"""
L298N Motor Driver
"""

import RPi.GPIO as GPIO
import time
from argparse import ArgumentParser as Args

GPIO.setwarnings(True)

# Set up GPIO pins
GPIO.setmode(GPIO.BCM)

IN1 = 40
IN2 = 39
IN3 = 20
IN4 = 21

pins = [IN1, IN2, IN3, IN4]

for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)

# Set up PWM
pwm = GPIO.PWM(IN1, 100)

# Main loop
while True:
    direction = input("Direction (f, b, l, r): ")
    # speed = int(input("Speed (0-100): ")
    speed = 100
    if direction == 'f':
        GPIO.output(IN1, 1)
        GPIO.output(IN2, 0)
        GPIO.output(IN3, 1)
        GPIO.output(IN4, 0)
        pwm.ChangeDutyCycle(speed)
    elif direction == 'b':
        GPIO.output(IN1, 0)
        GPIO.output(IN2, 1)
        GPIO.output(IN3, 0)
        GPIO.output(IN4, 1)
        pwm.ChangeDutyCycle(speed)
    elif direction == 'l':
        GPIO.output(IN1, 0)
        GPIO.output(IN2, 1)
        GPIO.output(IN3, 1)
        GPIO.output(IN4, 0)
        pwm.ChangeDutyCycle(speed)
    elif direction == 'r':
        GPIO.output(IN1, 1)
        GPIO.output(IN2, 0)
        GPIO.output(IN3, 0)
        GPIO.output(IN4, 1)
        pwm.ChangeDutyCycle(speed)
    else:
        break

GPIO.output(IN1, 0)
GPIO.output(IN2, 0)
GPIO.output(IN3, 0)
GPIO.output(IN4, 0)
pwm.stop()
GPIO.cleanup()
