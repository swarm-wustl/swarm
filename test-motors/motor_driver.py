import RPi.GPIO as GPIO
import time

# Set the GPIO pins for the motor driver
IN1 = 15
IN2 = 13
ENA = 11

# Set the GPIO pins as output
GPIO.setmode(GPIO.BOARD)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)

# Stop the motor
GPIO.output(ENA, GPIO.LOW)

# Move the motor forward
GPIO.output(IN1, GPIO.HIGH)
GPIO.output(IN2, GPIO.LOW)

try:  
    while True:
        GPIO.output(ENA, GPIO.HIGH)
        # Wait for 5 seconds
        time.sleep(5)

        GPIO.output(ENA, GPIO.HIGH)
        # Wait for 5 seconds
        time.sleep(5)

finally:  
    GPIO.cleanup() # this ensures a clean exit 
