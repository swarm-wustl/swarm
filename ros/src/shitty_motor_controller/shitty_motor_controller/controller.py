import rclpy
from rclpy.node import Node

import time

from geometry_msgs.msg import Twist

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)

def motor_init (in1, in2, en, freq, dutycycle):
   GPIO.setup(in1,GPIO.OUT)
   GPIO.setup(in2,GPIO.OUT)
   GPIO.setup(en,GPIO.OUT)
   GPIO.output(in1,GPIO.LOW)
   GPIO.output(in2,GPIO.LOW)
   pwm_pin=GPIO.PWM(en,freq)
   pwm_pin.start(dutycycle)
   return pwm_pin

def motor_pwm_change(pwm_pin, dutycycle):
   pwm_pin.start(dutycycle)

def motor_direction(in1, in2, direction, debug=False):     
   # direction -1 -backwards, 0 - stop, 1 - forward
   if (direction < 0):
      if debug: print ('Set backward')
      GPIO.output(in1,GPIO.LOW)
      GPIO.output(in2,GPIO.HIGH)
   elif ( direction == 0 ):
      if debug: print ('stopped')
      GPIO.output(in1,GPIO.LOW)
      GPIO.output(in2,GPIO.LOW)
   else: 
      if debug: print ('Set forward')
      GPIO.output(in1,GPIO.HIGH)
      GPIO.output(in2,GPIO.LOW)

def movingAvg(arr, position, numvals=3, wrap=1):
    # default to 3 pt moving average with wrap around on getting values 
    # arr       - array
    # posistion - start from this point on averages
    # numvals   - Number of values in moving average, default of 3
    # wrap      - wrap around to top or bottom of array if 1 (default), no if 0
    sumvals    = 0
    count      = 0    
    array_size = len(arr)
    # if less than numvals data, then just use what is available
    for i in range(numvals):
        # add an item to the list
        if (position - i >= 0 and position - 1 < array_size):
            sumvals = sumvals + arr[(position - i)]
            count   = count + 1
        # wrap backwards, goes to top of array, works in python
        elif (position - i < 0 and wrap == 1): 
            sumvals = sumvals + arr[(position - i)]
            count   = count + 1
        # wrap around to bottom of array with mod
        elif (position - i > array_size and wrap == 1):
            sumvals = sumvals + arr[(position - i)%array_size]
            count   = count + 1
    return sumvals/count

class Controller(Node):

    def __init__(self):
        super().__init__('controller')
        self.subscription = self.create_subscription(
            Twist,
            '/diff_cont/cmd_vel_unstamped',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

        self.target_left_speed = 0
        self.target_right_speed = 0

        # Motor 1
        self.in1A = 36
        self.in2A = 38
        self.enA  = 32
        self.c1 = 24
        self.c2 = 26

        # Motor 2
        self.in1B = 35
        self.in2B = 37
        self.enB  = 33

        GPIO.setup(self.c1, GPIO.IN)
        GPIO.setup(self.c2, GPIO.IN)

        GPIO.setwarnings(False)

        self.pwm_pinA = motor_init(self.in1A, self.in2A, self.enA, 1000, 50)
        time.sleep(0.025)
        self.pwm_pinB = motor_init(self.in1B, self.in2B, self.enB, 1000, 50)
        time.sleep(0.25)


    def listener_callback(self, msg):
        x_vel = msg.linear.x
        z_ang = msg.angular.z

        # diff drive kinematics
        left_speed = x_vel - z_ang
        right_speed = x_vel + z_ang

        # update target speeds by 10% of the difference
        self.target_left_speed += 0.1 * (left_speed - self.target_left_speed)
        self.target_right_speed += 0.1 * (right_speed - self.target_right_speed)

        # set motor speeds
        motor_pwm_change(self.pwm_pinA, int(abs(self.target_left_speed))*10)
        motor_pwm_change(self.pwm_pinB, int(abs(self.target_right_speed))*10)

        # set motor directions
        motor_direction(self.in1A, self.in2A, 1 if self.target_left_speed > 0 else -1)
        motor_direction(self.in1B, self.in2B, 1 if self.target_right_speed > 0 else -1)


def main(args=None):
    rclpy.init(args=args)

    controller = Controller()

    rclpy.spin(controller)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    controller.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
