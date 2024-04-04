import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
Motor1A= 13
Motor2A = 15
Motor1EN = 11

GPIO.setup(Motor1A, GPIO.OUT)
GPIO.setup(Motor2A, GPIO.OUT)
GPIO.setup(Motor1EN, GPIO.OUT)

def forward():
    GPIO.output(Motor1A, GPIO.HIGH)
    GPIO.output(Motor2A, GPIO.LOW)

def reverse():
    GPIO.output(Motor1A, GPIO.LOW)
    GPIO.output(Motor2A, GPIO.HIGH)

def ramp_up():
    pwm.start(80)
    for i in range(80, 110, 10):
        pwm.ChangeDutyCycle(i)
        print("{0}%".format(i))
        time.sleep(5)

pwm = GPIO.PWM(Motor1EN, 1000)

try:  
    while True:
        forward()
        ramp_up()
        pwm.stop()
        time.sleep(1)
        reverse()
        ramp_up()
        pwm.stop()
        time.sleep(1)

finally:  
    GPIO.cleanup() # this ensures a clean exit 
