# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 15:44:45 2024

@author: Wayne
"""

# Import libraries
import RPi.GPIO as GPIO
import time
import argparse

# Define GPIO pins based on BCM numbering
MotFwd = 17  # Motor Forward pin (BCM pin 18)
MotRev = 22 # Motor Reverse pin (BCM pin 23)
encoderPin1 = 5  # Encoder Output 'A' (BCM pin 24)
encoderPin2 = 6  # Encoder Output 'B' (BCM pin 25)

lastEncoded = 0
encoderValue = 0
encoderValues = [] # List to store encouder values 

# Command Line Arguments 
def parseArguments():
    parser = argparse.ArgumentParser(description='Motor control with encoder feedback.')
    parser.add_argument('-t', '--testDuration', type=int, default=10, help='Test duration in seconds')
    parser.add_argument('-s', '--spinDuration', type=int, default=5, help='Spin duration for each direction in seconds')
    return parser.parse_args()


# GPIO Raspb-PI Set up 
def setupGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(MotFwd, GPIO.OUT)
    GPIO.setup(MotRev, GPIO.OUT)
    GPIO.setup(encoderPin1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(encoderPin2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    # These lines of code indirectly call updateEncoder() through the GPIO event detection 
    # this is how data is being constantly transmitted into the program. 
    GPIO.add_event_detect(encoderPin1, GPIO.BOTH, callback=updateEncoder)
    GPIO.add_event_detect(encoderPin2, GPIO.BOTH, callback=updateEncoder)

# Read and interpret signals from rotary encoder attached to motors
# Funciton Tracks the position or rotation count of the motor shaft. 
def updateEncoder(channel):
    global lastEncoded, encoderValue
    MSB = GPIO.input(encoderPin1)
    LSB = GPIO.input(encoderPin2)

    encoded = (MSB << 1) | LSB
    sum = (lastEncoded << 2) | encoded

    if sum == 0b1101 or sum == 0b0100 or sum == 0b0010 or sum == 0b1011:
        encoderValue -= 1
    if sum == 0b1110 or sum == 0b0111 or sum == 0b0001 or sum == 0b1000:
        encoderValue += 1

    lastEncoded = encoded
    encoderValues.append(encoderValue)  # Append the current encoder value to the list

def main():
    args = parseArguments()
    setupGPIO()

    startTime = time.time()
    elapsedTime = 0

    while elapsedTime < args.testDuration:
        currentTime = time.time()
        elapsedTime = currentTime - startTime

        # Forward
        if elapsedTime % args.spinDuration < args.spinDuration:
            GPIO.output(MotFwd, GPIO.LOW)
            GPIO.output(MotRev, GPIO.HIGH)
            print(f"Forward  {encoderValue}")

        time.sleep(0.1)  # Reduce delay to check condition more frequently

    print("Test completed.")
    print("Encoder values collected:", encoderValues)  # Print the collected encoder values
    GPIO.cleanup()

if __name__ == "__main__":
    main()