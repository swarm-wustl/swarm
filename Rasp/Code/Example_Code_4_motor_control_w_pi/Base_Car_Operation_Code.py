''' 
Robotics Class ESE 3050 

Developers: 
    Edgar Sarceno 
    Russell Harounian 
    etc. 
Created: 
    Dec. 12. 2023. 02:40:00 pm, CT
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

GPIO.setwarnings(False)

print("Starting Initilization")
# Set up GPIO pins
motor_pins = [17, 22, 23, 24]  # 17 & 22 pins for 'front' motors, 23 & 24 for back motors.  
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin-numbering scheme
for pin in motor_pins:
    GPIO.setup(pin, GPIO.OUT)

# Set up individial Motor Pin Variables
motor_pin_1 = motor_pins[0] 
motor_pin_2 = motor_pins[1] 
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
# Pin 4 Left direction, 3 right direction 


# Function to control individual motors
def control_motor(pin, duration, pwm_value):
    # Initialize PWM on the specified pin with a frequency of 100Hz
    pwm = GPIO.PWM(pin, 100)
    # Start the motor with the user-specified PWM value
    pwm.start(pwm_value)
    print(f"Running motor on pin {pin} with PWM {pwm_value} for {duration} seconds")
    time.sleep(duration)
    pwm.stop()

# Main loop
while True:
    cur_time = time.time()
    if cur_time - start_time > args.time:
        print("Time limit reached, exiting.")
        break

    # Prompt for motor command
    print("_______________________________________________________")
    print("Left: pin 2 forward, pin 1 backward")
    print("Right: pin 4 forward, pin 3 backward ")
    command = input("Enter motor command (1, 2, 3, 4) or 'exit': ").strip()
    
    if command == 'exit':
        break
    elif command in ['1', '2', '3', '4']:
        motor_pin = motor_pins[int(command) - 1]

        # Prompt for PWM value
        pwm_value = input("Enter PWM value (0-100): ").strip()
        
        try:
            pwm_value = int(pwm_value)
            if 0 <= pwm_value <= 100:
                control_motor(motor_pin, args.spin_duration, pwm_value)
            else:
                print("Invalid PWM value. Please enter a value between 0 and 100.")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

    else:
        print("Invalid command.")

# Clean up GPIO pins before exiting
GPIO.cleanup()
print("Program terminated.")