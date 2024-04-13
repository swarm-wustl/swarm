# -*- coding: utf-8 -*-
"""
Created on Sat Apr  6 14:27:39 2024

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

def forward(motor):
    """Function to set the motor direction to forward."""
    if motor == 1:
        GPIO.output(Motor1A, GPIO.HIGH)
        GPIO.output(Motor1B, GPIO.LOW)
        print("Motor 1 set to forward.")
    elif motor == 2:
        GPIO.output(Motor2A, GPIO.HIGH)
        GPIO.output(Motor2B, GPIO.LOW)
        print("Motor 2 set to forward.")

def reverse(motor):
    """Function to set the motor direction to reverse."""
    if motor == 1:
        GPIO.output(Motor1A, GPIO.LOW)
        GPIO.output(Motor1B, GPIO.HIGH)
        print("Motor 1 set to reverse.")
    elif motor == 2:
        GPIO.output(Motor2A, GPIO.LOW)
        GPIO.output(Motor2B, GPIO.HIGH)
        print("Motor 2 set to reverse.")

def ramp_up(pwm, motor_number):
    """Function to gradually increase the motor's speed."""
    pwm.start(80)  # Start PWM with 80% duty cycle
    print(f"Ramping up Motor {motor_number}: Starting at 80% power.")
    for i in range(80, 110, 10):  # Increase duty cycle from 80% to 100% in steps of 10%
        pwm.ChangeDutyCycle(i)
        if i > 100:
            print(f"Motor {motor_number} at maximum power: 100%.")
        else:
            print(f"Motor {motor_number} power level: {i}%.")
        time.sleep(5)

pwm1 = GPIO.PWM(Motor1EN, 1000)  # PWM instance for Motor 1
pwm2 = GPIO.PWM(Motor2EN, 1000)  # PWM instance for Motor 2

# Motor 1 forward and ramp up
# forward(1)
# ramp_up(pwm1, 1)
# pwm1.stop()

# Motor 2 forward and ramp up
forward(2)
ramp_up(pwm2, 2)
pwm2.stop()

time.sleep(1)

# Motor 1 reverse and ramp up
reverse(1)
ramp_up(pwm1, 1)
pwm1.stop()

# Motor 2 reverse and ramp up
reverse(2)
ramp_up(pwm2, 2)
pwm2.stop()

GPIO.cleanup()  # Clean up GPIO to ensure a clean exit
