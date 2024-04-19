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

class Controller(Node):

    def __init__(self):
        super().__init__('controller')
        self.subscription = self.create_subscription(
            Twist,
            '/diff_cont/cmd_vel_unstamped',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

        # publish encoder data
        self.publisher = self.create_publisher(Twist, '/left_encoder', 10)
        # self.publisher = self.create_publisher(Twist, '/left_encoder', 10)

        # timer
        self.timer = self.create_timer(0.01, self.timer_callback)

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

        first_val = GPIO.input(self.c1)
        self.look_for_1 = not first_val
        self.n = 10
        self.i = 0
        self.transitionTimes = [0] * self.n
        self.startTime = time.time()


    def listener_callback(self, msg):
        x_vel = msg.linear.x
        z_ang = msg.angular.z

        # diff drive kinematics
        left_speed = x_vel - z_ang
        right_speed = x_vel + z_ang

        # slowly approach target speeds
        self.target_left_speed = 0.95*self.target_left_speed + 0.05*left_speed
        self.target_right_speed = 0.95*self.target_right_speed + 0.05*right_speed

    def timer_callback(self):
        # set motor speeds
        motor1 = int(abs(self.target_left_speed)*100)
        motor2 = int(abs(self.target_right_speed)*100)
        motor1 = min(90, motor1) if motor1 > 20 else 0
        motor2 = min(90, motor2) if motor2 > 20 else 0

        motor_pwm_change(self.pwm_pinA, motor1)
        motor_pwm_change(self.pwm_pinB, motor2)

        # set motor directions
        motor_direction(self.in1A, self.in2A, 1 if self.target_left_speed > 0 else -1)
        motor_direction(self.in1B, self.in2B, 1 if self.target_right_speed > 0 else -1)

        # decay motor speeds
        self.target_left_speed *= 0.7
        self.target_right_speed *= 0.7

        # get encoder data
        c1_val = GPIO.input(self.c1)
        # c2_val = GPIO.input(self.c2)

        if self.look_for_1 and c1_val == 0:
            self.transitionTimes[self.i%self.n] = self.startTime - time.time()
            self.look_for_1 = False
            self.i += 1
        elif not self.look_for_1 and c1_val == 1:
            self.transitionTimes[self.i%self.n] = self.startTime - time.time()
            self.look_for_1 = True
            self.i += 1

        # calculate speeds
        if self.i > self.n:
            speed = 1/(self.transitionTimes[(self.i-1)%self.n] - self.transitionTimes[(self.i-self.n)%self.n])
        else:
            speed = 0

        self.get_logger().info('Speed: %f' % speed)


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
