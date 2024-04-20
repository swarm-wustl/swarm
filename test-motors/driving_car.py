import argparse
import time
import matplotlib.pyplot as plt

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
import motor_funcs as motor

# Motor A
in1A = 36
in2A = 38
enA  = 32
c1A = 26
c2A = 24

# Motor B
in1B = 35
in2B = 37
enB  = 33
c1B = 31
c2B = 29

GPIO.setup(c1A, GPIO.IN)
GPIO.setup(c2A, GPIO.IN)

GPIO.setup(c1B, GPIO.IN)
GPIO.setup(c2B, GPIO.IN)

GPIO.setwarnings(False)

# Adds arguments
parser = argparse.ArgumentParser(description="Collect rotational data.")

parser.add_argument("--time", default = 4, type=float, action="store", help  = "Duration of program.")
parser.add_argument("--enSample", default = 1, type = float, action = "store", help = "Delay between readings in micro seconds.")
parser.add_argument("--speedCalc", default = 10, type = float, action = "store", help = "Delay between RPS calculators in msec (Default is 0.1s).")
parser.add_argument("--duty", default = 50., type = float, action= "store", help= "Desired RPS for the motor")
parser.add_argument("--debug", action= 'store_true', help= "Specify if debug statements are printed")

args = parser.parse_args()

# Servo Setup
# Define pin, frequency and duty cycle
servo_pin  = 40
freq = 50

GPIO.setup(servo_pin, GPIO.OUT)
servo_pwm = GPIO.PWM(servo_pin, freq) 
servo_pwm.start(6)
time.sleep(0.2)

# Motor init
pwm_pinA = motor.motor_init(in1A, in2A, enA, 1000, args.duty)
time.sleep(0.1)
pwm_pinB = motor.motor_init(in1B, in2B, enB, 1000, args.duty)
time.sleep(0.1)
motor.motor_direction(in1A, in2A, 1)
time.sleep(0.1)
motor.motor_direction(in1B, in2B, 1)
time.sleep(0.1)

# Setup for delta timing
startTime = time.time()
currentTime = startTime

# Variable for how far back we want to calc speeds
n = 20
a = 0
b = 0

# Time for encoder data collection
enTime = startTime
# Time for speed calculations
calcTime = startTime

transitionTimesA = [0] * n
transitionTimesB = [0] * n
allSpeedsA = []
allSpeedsB = []
allTimes = []

# PID errors
error = 0
sum_error = 0
prev_error = 0

# PID Coefs
Kp = 1
Ki = 0.1
Kd = 0

# Direction Variables
followA = True # When true, it can turn left. When false it can turn right
reduction = 0.75 # fraction of speed of the follow motor

# If debug, save all data
if args.debug:
    encoder1AData = []
    encoder2AData = []

    encoder1BData = []
    encoder2BData = []

    times = []

firstValA = GPIO.input(c1A)
if firstValA == 0:
    lookFor1A = True
else:
    lookFor1A = False

firstValB = GPIO.input(c1A)
if firstValB == 0:
    lookFor1B = True
else:
    lookFor1B = False

while currentTime - startTime < args.time:

    if currentTime - enTime >= args.enSample * 1e-6:
            
        if args.debug:

            encoder1AData.append(GPIO.input(c1A))
            encoder2AData.append(GPIO.input(c2A))

            encoder1BData.append(GPIO.input(c1B))
            encoder2BData.append(GPIO.input(c2B))

            times.append(currentTime - startTime)

        c1AVal = GPIO.input(c1A)
        c2AVal = GPIO.input(c2A)

        c1BVal = GPIO.input(c1B)
        c2BVal = GPIO.input(c2B)
        
        if lookFor1A and c1AVal == 1:
            transitionTimesA[a%n] = currentTime - startTime
            lookFor1A = False
            a += 1
        elif not lookFor1A and c1AVal == 0:
            transitionTimesA[a%n] = currentTime - startTime
            lookFor1A = True
            a += 1

        if lookFor1B and c1BVal == 1:
            transitionTimesB[b%n] = currentTime - startTime
            lookFor1B = False
            b += 1
        elif not lookFor1B and c1BVal == 0:
            transitionTimesB[b%n] = currentTime - startTime
            lookFor1B = True
            b += 1
            
        enTime = currentTime

    if currentTime - calcTime >= args.speedCalc * 1e-3:

        if a > n:
            speedA = 1/(transitionTimesA[(a-1)%n] - transitionTimesA[(a-n)%n])
        else:
            speedA = 0

        if b > n:
            speedB = 1/(transitionTimesB[(b-1)%n] - transitionTimesB[(b-n)%n])
        else:
            speedB = 0

        allSpeedsA.append(speedA)
        allSpeedsB.append(speedB)
        allTimes.append(currentTime - startTime)

        calcTime = currentTime

        ### PID control to match the speeds
        # Set motor 1 as the "goal" speed and make motor 2 match it.

        if followA:
            prev_error = error
            error = speedA * reduction - speedB
            sum_error += error

            pwmB = Kp * error + Ki * sum_error + Kd * (error - prev_error) + args.duty + 10

            if pwmB > 100:
                pwmB = 100
            elif pwmB < 0:
                pwmB = 0

            motor.motor_pwm_change(pwm_pinA, args.duty)
            motor.motor_pwm_change(pwm_pinB, pwmB)
        else:
            prev_error = error
            error = speedB * reduction - speedA
            sum_error += error

            pwmA = Kp * error + Ki * sum_error + Kd * (error - prev_error) + args.duty + 10

            if pwmA > 100:
                pwmA = 100
            elif pwmA < 0:
                pwmA = 0

            motor.motor_pwm_change(pwm_pinA, pwmA)
            motor.motor_pwm_change(pwm_pinB, args.duty)



    currentTime = time.time()


with open(f'speed_data.txt', 'w') as f:

    f.write(f'{"Speed A"} \t {"Speed B"} \t {"Time"}\n')

    for i in range(len(allSpeedsA)):
        f.write(f'{allSpeedsA[i]} \t {allSpeedsB[i]} \t {allTimes[i]}\n')

plt.figure()
plt.plot(allTimes, allSpeedsA, label="Motor A Speed")
plt.plot(allTimes, allSpeedsB, label="Motor B Speed")
plt.grid()                          # show the grid
plt.xlabel('time - sec')
plt.ylabel('Speed Calc')
plt.savefig('motorSpeed.png')

if args.debug:
    with open(f'encoder_data.txt', 'w') as f:

        f.write(f'{"En 1 A"} \t {"En 2 A"} \t {"En 1 B"} \t {"En 2 B"} \t {"Time"}\n')

        for i in range(len(encoder1AData)):
            f.write(f'{encoder1AData[i]} \t \t {encoder2AData[i]} \t \t {encoder1BData[i]} \t \t {encoder2BData[i]} \t \t {times[i]:.4f}\n')


motor.motor_pwm_change(pwm_pinA, 0)
motor.motor_pwm_change(pwm_pinB, 0)
time.sleep(0.5)

servo_pwm.start(7)
time.sleep(0.1)

GPIO.cleanup()