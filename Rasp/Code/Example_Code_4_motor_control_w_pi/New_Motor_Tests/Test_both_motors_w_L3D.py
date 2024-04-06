# -*- coding: utf-8 -*-
"""
Created on Sat Apr  6 14:27:39 2024

@author: Wayne
"""

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# Motor 1 setup
Motor1A = 23
Motor1B = 24
Motor1EN = 25

# Motor 2 setup
Motor2A = 22
Motor2B = 27
Motor2EN = 17

GPIO.setup(Motor1A, GPIO.OUT)
GPIO.setup(Motor1B, GPIO.OUT)
GPIO.setup(Motor1EN, GPIO.OUT)

GPIO.setup(Motor2A, GPIO.OUT)
GPIO.setup(Motor2B, GPIO.OUT)
GPIO.setup(Motor2EN, GPIO.OUT)

def forward(motor):
    if motor == 1:
        GPIO.output(Motor1A, GPIO.HIGH)
        GPIO.output(Motor1B, GPIO.LOW)
    elif motor == 2:
        GPIO.output(Motor2A, GPIO.HIGH)
        GPIO.output(Motor2B, GPIO.LOW)

def reverse(motor):
    if motor == 1:
        GPIO.output(Motor1A, GPIO.LOW)
        GPIO.output(Motor1B, GPIO.HIGH)
    elif motor == 2:
        GPIO.output(Motor2A, GPIO.LOW)
        GPIO.output(Motor2B, GPIO.HIGH)

def ramp_up(pwm):
    pwm.start(80)
    for i in range(80, 110, 10):
        pwm.ChangeDutyCycle(i)
        print("{0}%".format(i))
        time.sleep(5)

pwm1 = GPIO.PWM(Motor1EN, 1000)
pwm2 = GPIO.PWM(Motor2EN, 1000)

# Motor 1 forward and ramp up
forward(1)
ramp_up(pwm1)
pwm1.stop()

# Motor 2 forward and ramp up
forward(2)
ramp_up(pwm2)
pwm2.stop()

time.sleep(1)

# Motor 1 reverse and ramp up
reverse(1)
ramp_up(pwm1)
pwm1.stop()

# Motor 2 reverse and ramp up
reverse(2)
ramp_up(pwm2)
pwm2.stop()

GPIO.cleanup()