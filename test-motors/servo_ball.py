import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
import time




# Servo Setup (FOR SWARM PI FOUR!)
# Define pin, frequency and duty cycle
servo_pin  = 40
freq = 50

GPIO.setup(servo_pin, GPIO.OUT)
servo_pwm = GPIO.PWM(servo_pin, freq) 

servo_pwm.start(7)
time.sleep(1)

servo_pwm.start(3)
time.sleep(1)

servo_pwm.start(7)
time.sleep(1)