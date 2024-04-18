import argparse
import time
import matplotlib.pyplot as plt

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
import motor_funcs as motor

# Motor 1
in1A = 36
in2A = 38
enA  = 32
c1 = 24
c2 = 26

# Motor 2
in1B = 35
in2B = 37
enB  = 33


GPIO.setup(c1, GPIO.IN)
GPIO.setup(c2, GPIO.IN)

GPIO.setwarnings(False)

# Adds arguments
parser = argparse.ArgumentParser(description="Collect rotational data.")

parser.add_argument("--time", default = 4, type=float, action="store", help  = "Duration of program.")
parser.add_argument("--enSample", default = 1, type = float, action = "store", help = "Delay between readings in micro seconds.")
parser.add_argument("--speedCalc", default = 10, type = float, action = "store", help = "Delay between RPS calculators in msec (Default is 0.1s).")
parser.add_argument("--duty", default = 50., type = float, action= "store", help= "Desired RPS for the motor")
parser.add_argument("--debug", action= 'store_true', help= "Specify if debug statements are printed")


args = parser.parse_args()

pwm_pinA   = motor.motor_init(in1A, in2A, enA, 1000, args.duty)
time.sleep(0.025)
pwm_pinB   = motor.motor_init(in1B, in2B, enB, 1000, args.duty)
time.sleep(0.25)
motor.motor_direction(in1A, in2A, 1)
time.sleep(0.025)
motor.motor_direction(in1B, in2B, 1)
time.sleep(0.025)

# Setup for delta timing
startTime = time.time()
currentTime = startTime

# Variable for how far back we want to calc speeds
n = 10
i = 0

# Time for encoder data collection
enTime = startTime
# Time for speed calculations
calcTime = startTime

transitionTimes = [0] * n
allSpeeds = list()
allTimes = list()

# If debug, save all data
if args.debug:
    en1Data = list()
    en2Data = list()
    times = list()

firstVal = GPIO.input(c1)
if firstVal == 0:
    lookFor1 = True
else:
    lookFor1 = False

while currentTime - startTime < args.time:

    if currentTime - enTime >= args.enSample * 1e-6:
            
        if args.debug:
            en1Data.append(GPIO.input(c1))
            en2Data.append(GPIO.input(c2))
            times.append(currentTime - startTime)

        c1Val = GPIO.input(c1)
        c2Val = GPIO.input(c2)
        
        if lookFor1 and c1Val == 1:
            transitionTimes[i%n] = currentTime - startTime
            lookFor1 = False
            i += 1
        elif not lookFor1 and c1Val == 0:
            transitionTimes[i%n] = currentTime - startTime
            lookFor1 = True
            i += 1
            
        enTime = currentTime

    if currentTime - calcTime >= args.speedCalc * 1e-3:

        if i > n:
            speed = 1/(transitionTimes[(i-1)%n] - transitionTimes[(i-n)%n])
        else:
            speed = 0

        allSpeeds.append(speed)
        allTimes.append(currentTime - startTime)

        calcTime = currentTime

    currentTime = time.time()


with open(f'speed_data.txt', 'w') as f:

    f.write(f'{"Speed"} \t {"Time"}\n')

    for i in range(len(allSpeeds)):
        f.write(f'{allSpeeds[i]} \t {allTimes[i]}\n')

plt.figure()
plt.plot(allTimes, allSpeeds, label="Motor Speed")
plt.grid()                          # show the grid
plt.xlabel('time - sec')
plt.ylabel('Speed Calc')
plt.savefig('motorSpeed.png')

if args.debug:
    with open(f'encoder_data.txt', 'w') as f:

        f.write(f'{"En 1"} \t {"En 2"} \t {"Time"}\n')

        for i in range(len(en1Data)):
            f.write(f'{en1Data[i]} \t \t {en2Data[i]} \t \t {times[i]:.4f}\n')

GPIO.cleanup()