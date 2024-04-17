# -*- coding: utf-8 -*-
"""
Created on Sat Apr 6 14:27:39 2024
@author: Wayne
"""

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)  # Set GPIO numbering mode to BCM

# Motor 1 setup
Motor1A = 6  # Motor 1, Pin A
Motor1B = 26  # Motor 1, Pin B
Motor1EN = 16 # Motor 1, Enable Pin

# Motor 2 setup
Motor2A = 22  # Motor 2, Pin A
Motor2B = 27  # Motor 2, Pin B
Motor2EN = 17  # Motor 2, Enable Pin

# Setup GPIO pin directions for both motors
GPIO.setup(Motor1A, GPIO.OUT)
GPIO.setup(Motor1B, GPIO.OUT)
GPIO.setup(Motor1EN, GPIO.OUT)

GPIO.setup(Motor2A, GPIO.OUT)
GPIO.setup(Motor2B, GPIO.OUT)
GPIO.setup(Motor2EN, GPIO.OUT)

# PWM instances for both motors, set to 70% duty cycle
pwm1 = GPIO.PWM(Motor1EN, 1000)
pwm1.start(70)
pwm2 = GPIO.PWM(Motor2EN, 1000)
pwm2.start(70)

def forward(motor_number):
    """Function to set the motor direction to forward and run it at 70% power."""
    if motor_number == 1:
        GPIO.output(Motor1A, GPIO.HIGH)
        GPIO.output(Motor1B, GPIO.LOW)
        print("Motor 1 is running forward at 70% power.")
    elif motor_number == 2:
        GPIO.output(Motor2A, GPIO.HIGH)
        GPIO.output(Motor2B, GPIO.LOW)
        print("Motor 2 is running forward at 70% power.")

def reverse(motor_number):
    """Function to set the motor direction to reverse and run it at 70% power."""
    if motor_number == 1:
        GPIO.output(Motor1A, GPIO.LOW)
        GPIO.output(Motor1B, GPIO.HIGH)
        print("Motor 1 is running in reverse at 70% power.")
    elif motor_number == 2:
        GPIO.output(Motor2A, GPIO.LOW)
        GPIO.output(Motor2B, GPIO.HIGH)
        print("Motor 2 is running in reverse at 70% power.")

# Test each motor in forward and reverse directions
for motor_id in [1, 2]:
    # Test forward direction
    forward(motor_id)
    time.sleep(5)  # Run each test for 5 seconds

    # Test reverse direction
    reverse(motor_id)
    time.sleep(5)  # Run each test for 5 seconds

    # Stop the motor
    (pwm1 if motor_id == 1 else pwm2).stop()

GPIO.cleanup()  # Clean up GPIO to ensure a clean exit
