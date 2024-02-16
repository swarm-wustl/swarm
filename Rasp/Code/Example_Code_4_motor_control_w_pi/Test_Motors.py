''' 
Robotics Class ESE 3050 

Developers: 
    Edgar Sarceno 
    Russell Harounian 
    etc. 
Created: 
    Nov. 2. 2023. 03:42:00 pm, CT
'''

# Importing Libraries
import RPi.GPIO as GPIO
import time
from argparse import ArgumentParser as Args

# Set up command-line arguments
parser = Args(description='Robot Base Car Algorithm Search Pole.')
parser.add_argument('--time', type=int, default=10, help='Duration for the search in seconds')
parser.add_argument('--Starting_PWM', type=int, default =10, help='Starting PWM for the motors to over come friction')
parser.add_argument('--spin_duration', type=int, default = 10, help='How Long do you wish to run testing on each motor? ')
args = parser.parse_args()

GPIO.setwarnings(False

# Set up GPIO pins
motor_pins = [4, 17, 27, 22]  # 17 & 22 pins for 'front' motors, 23 & 24 for back motors.  
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin-numbering scheme
for pin in motor_pins:
    GPIO.setup(pin, GPIO.OUT)

# Set up individial Motor Pin Variables
motor_pin_1 = motor_pins[0]
motor_pin_2 = motor_pins[1] # NO
motor_pin_3 = motor_pins[2]
motor_pin_4 = motor_pins[3] 



# Delta timing mechanism
start_time = time.time()
cur_time = start_time
spin_duration = 5  # Duration in seconds # Just a test 


# Set up all Pins 

# Set up H-BRidge Motor Pins 
GPIO.setup(motor_pin_1 , GPIO.OUT)
GPIO.setup(motor_pin_2 , GPIO.OUT)
GPIO.setup(motor_pin_3 , GPIO.OUT)
GPIO.setup(motor_pin_4 , GPIO.OUT)



# Set up a 2 second Delay for Initialization
time.sleep(2) 

print("Initilization Finished")


# Set up PWM
# Pin 2 forward direction, 1  backward direction 
# Pin 3 left direction, 4 right direction 


# Initialize a variable to keep track of the current PWM pin
current_pwm_pin = motor_pin_2

# Initialize PWM on the first motor pin before the loop
pwm = GPIO.PWM(current_pwm_pin, 100)  # Starting with motor_pin_2
print(f'Defining PWM with {motor_pin_2}')

# Start the motor
# print("Starting Motor before testing Sequence: ")
# pwm.start(70)  # Start PWM with 70% duty cycle 

print("Starting Testing Sequence using Delta Timing Loop. ")

# Main loop
while (start_time + args.time > cur_time):
    cur_time = time.time()

    # Forward direction - using motor_pin_2
    if cur_time - start_time < spin_duration:
        if current_pwm_pin != motor_pin_2:
            pwm.stop()
            pwm = GPIO.PWM(motor_pin_2, 100)
            pwm.start(70)
            current_pwm_pin = motor_pin_2
        print("Testing forward direction with motor_pin_2")

    # Backward direction - using motor_pin_1
    elif cur_time - start_time < 2 * spin_duration:
        if current_pwm_pin != motor_pin_1:
            pwm.stop()
            pwm = GPIO.PWM(motor_pin_1, 100)
            pwm.start(70)
            current_pwm_pin = motor_pin_1
        print("Testing backward direction with motor_pin_1")

    # Left direction - using motor_pin_3
    elif cur_time - start_time < 3 * spin_duration:
        if current_pwm_pin != motor_pin_3:
            pwm.stop()
            pwm = GPIO.PWM(motor_pin_3, 100)
            pwm.start(70)
            current_pwm_pin = motor_pin_3
        print("Testing left direction with motor_pin_3")

    # Right direction - using motor_pin_4
    elif cur_time - start_time < 4 * spin_duration:
        if current_pwm_pin != motor_pin_4:
            pwm.stop()
            pwm = GPIO.PWM(motor_pin_4, 100)
            pwm.start(70)
            current_pwm_pin = motor_pin_4
        print("Testing right direction with motor_pin_4")

    # Stop the motor after testing all directions
    else:
        pwm.stop()
        break

    pwm.start(70)


pwm.start(70)



# Stop the motor
pwm.stop()


print("Loop Ended")
# Clean up GPIO pins before exiting
GPIO.cleanup()
