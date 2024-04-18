import argparse
import time
import matplotlib.pyplot as plt

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
import motor_funcs as motor

in1 = 13 #37
in2 = 15 #31
en  = 11 #36

c1 = 16
c2 = 18

GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(en, GPIO.OUT)
GPIO.setup(c1, GPIO.OUT)
GPIO.setup(c2, GPIO.OUT)

GPIO.output(in1,GPIO.HIGH)
GPIO.output(in2,GPIO.LOW)
GPIO.output(en,GPIO.HIGH)
GPIO.output(c1,GPIO.LOW)
GPIO.output(c2,GPIO.LOW)

time.sleep(5)

GPIO.cleanup()