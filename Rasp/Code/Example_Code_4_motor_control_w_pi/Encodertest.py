
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 15:44:45 2024

@author: Wayne & Sam
"""

# Import libraries
import RPi.GPIO as GPIO
import time
import argparse
import matplotlib.pyplot as plt
import numpy as np

# Define GPIO pins based on BCM numbering
MotFwd = 17  # Motor Forward pin (BCM pin 18)
MotRev = 23 # Motor Reverse pin (BCM pin 23)
encoderPin1 = 24  # Encoder Output 'A' (BCM pin 24)
encoderPin2 = 25  # Encoder Output 'B' (BCM pin 25)

lastEncoded = 0
encoderValue = 0
encoderValues = [] # List to store encouder values 
timeStamps = []  # List to store time stamps




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
    global lastEncoded, encoderValue, startTime   
    
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
    currentTime = time.time() - startTime  # Calculate elapsed time since start
    timeStamps.append(currentTime)  # Append the current time to the timeStamps list

def main():
    global startTime 
    
    print("Start Sequence: ")
    args = parseArguments()
    setupGPIO()

    startTime = time.time()
    elapsedTime = 0

    forward = True  # Initialize direction flag

    while elapsedTime < args.testDuration:
        currentTime = time.time()
        elapsedTime = currentTime - startTime

        # Check if it's time to switch direction
        if int(elapsedTime / args.spinDuration) % 2 == 0:
            if forward:
                GPIO.output(MotFwd, GPIO.HIGH)
                GPIO.output(MotRev, GPIO.LOW)
                print(f"Forward  Time: {elapsedTime} || Data: {encoderValue}")
            else:
                GPIO.output(MotFwd, GPIO.LOW)
                GPIO.output(MotRev, GPIO.HIGH)
                print(f"Reverse  Time: {elapsedTime} || Data: {encoderValue}")
        else:
            # Time to switch direction
            forward = not forward

        time.sleep(0.1)  # Reduce delay to check condition more frequently

    print("Test completed.")
    # Cleanup and other code follows...

 
def moving_average(data, window_size):
    """Calculate the moving average using a simple sliding window algorithm."""
    
    
    return np.convolve(data, np.ones(window_size) / window_size, mode='valid')

def plot_data(timeStamps, encoderValues, window_size=10):
    global startTime
    
    
    """Plot the raw data, moving average, noise, and deviation, and save the plots."""
    rawEncoderData = np.array(encoderValues)
    timeArray = np.array(timeStamps)
    
    # 1. Plot Time vs Encoder Data
    plt.figure(figsize=(10, 8))
    plt.subplot(4, 1, 1)
    plt.plot(timeArray, rawEncoderData, label='Raw Encoder Data')
    plt.xlabel('Time (s)')
    plt.ylabel('Encoder Value')
    plt.title('Time vs Encoder Data')
    plt.legend()
    plt.savefig('Time_vs_Encoder_Data.png')
    plt.close()  # Close the plot to prevent it from displaying

    # 2. Moving Average
    movingAvg = moving_average(rawEncoderData, window_size)
    timeForMovingAvg = timeArray[:len(movingAvg)]  # Adjust time array for moving average plot
    plt.figure(figsize=(10, 8))
    plt.plot(timeForMovingAvg, movingAvg, label='Moving Average', color='orange')
    plt.xlabel('Time (s)')
    plt.ylabel('Encoder Value')
    plt.title('Moving Average of Encoder Data')
    plt.legend()
    plt.savefig('Moving_Average_of_Encoder_Data.png')
    plt.close()

    # 3. Noise Plot
    extendedMovingAvg = np.interp(timeArray, timeForMovingAvg, movingAvg)
    noise = rawEncoderData - extendedMovingAvg
    plt.figure(figsize=(10, 8))
    plt.plot(timeArray, noise, label='Noise', color='green')
    plt.xlabel('Time (s)')
    plt.ylabel('Noise')
    plt.title('Noise in Encoder Data')
    plt.legend()
    plt.savefig('Noise_in_Encoder_Data.png')
    plt.close()

    # 4. Deviation Data Plot
    deviationArrayData = np.abs(np.diff(rawEncoderData))
    timeForDeviation = timeArray[1:]  # Adjust time array for deviation plot
    plt.figure(figsize=(10, 8))
    plt.plot(timeForDeviation, deviationArrayData, label='Deviation', color='red')
    plt.xlabel('Time (s)')
    plt.ylabel('Deviation')
    plt.title('Deviation of Encoder Data')
    plt.legend()
    plt.savefig('Deviation_of_Encoder_Data.png')
    plt.close()
    
    
if __name__ == "__main__":
    print("Running Main Sequence: ")
    main() 
    
    print("Starting Plotting Sequence: ")
    # After main function completes, call the plotting function
    
    if len(timeStamps) != len(encoderValues):
        print(f"Mismatch in lengths: TimeStamps={len(timeStamps)}, EncoderValues={len(encoderValues)}")
        min_length = min(len(timeStamps), len(encoderValues))
        timeStamps = timeStamps[:min_length]
        encoderValues = encoderValues[:min_length]
    # Optionally adjust the arrays here

    plot_data(timeStamps, encoderValues, window_size=10)
    print("Ploting sequence Completed. ")
    
