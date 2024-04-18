import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
Motor1A= 17
Motor2A = 27
Motor1EN = 16



'''

Left motor: 
Motor1A= 26
Motor2A = 6
Motor1EN = 5


Motor1A = 6  # Motor 1, Pin A
Motor1B = 26  # Motor 1, Pin B
Motor1EN = 16 # Motor 1, Enable Pin

# Motor 2 setup
Motor2A = 22  # Motor 2, Pin A
Motor2B = 27  # Motor 2, Pin B
Motor2EN = 12  # Motor 2, Enable Pin
'''

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
print("Testing Motor1 Forward: ")
forward()
ramp_up()
pwm.stop()
time.sleep(1)
print("Testing Motor1 Reverse: ")
reverse()
ramp_up()
pwm.stop()



GPIO.cleanup()
