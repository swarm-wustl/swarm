import rclpy
from rclpy.node import Node

import time

from geometry_msgs.msg import Twist
from std_msgs.msg import Float32

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
        print('sub')

        # publish encoder data
        self.publisher_left = self.create_publisher(Float32, '/left_encoder', 10)
        self.publisher_right = self.create_publisher(Float32, '/right_encoder', 10)

        # timer
        self.timer = self.create_timer(0.01, self.timer_callback)

        self.target_left_speed = 0
        self.target_right_speed = 0

        # Motor 1
        self.in1A = 36
        self.in2A = 38
        self.enA  = 32
        self.c1A = 24
        self.c2A = 26

        # Motor 2
        self.in1B = 35
        self.in2B = 37
        self.enB  = 33
        self.c1B = 31
        self.c2B = 29

        GPIO.setup(self.c1A, GPIO.IN)
        GPIO.setup(self.c2A, GPIO.IN)

        GPIO.setup(self.c1B, GPIO.IN)
        GPIO.setup(self.c2B, GPIO.IN)

        GPIO.setwarnings(False)

        self.pwm_pinA = motor_init(self.in1A, self.in2A, self.enA, 1000, 50)
        time.sleep(0.025)
        self.pwm_pinB = motor_init(self.in1B, self.in2B, self.enB, 1000, 50)
        time.sleep(0.25)
        print('init')

        self.look_for_1A = True
        self.look_for_1B = True
        self.n = 20
        self.a = 0
        self.b = 0
        self.transitionTimesA = [0] * self.n
        self.transitionTimesB = [0] * self.n
        self.startTime = time.time()
        self.currentTime = self.startTime

        self.error = 0
        self.prev_error = 0
        self.sum_error = 0

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
        c1a_val = GPIO.input(self.c1A)
        c1b_val = GPIO.input(self.c1B)

        if self.look_for_1A and c1a_val == 0:
            self.transitionTimesA[self.a%self.n] = self.startTime - time.time()
            self.look_for_1A = False
            self.a += 1
        elif not self.look_for_1A and c1a_val == 1:
            self.transitionTimesA[self.a%self.n] = self.startTime - time.time()
            self.look_for_1A = True
            self.a += 1

        if self.look_for_1B and c1b_val == 0:
            self.transitionTimesB[self.b%self.n] = self.startTime - time.time()
            self.look_for_1B = False
            self.b += 1
        elif not self.look_for_1B and c1b_val == 1:
            self.transitionTimesB[self.b%self.n] = self.startTime - time.time()
            self.look_for_1B = True
            self.b += 1

        # calculate speeds
        if self.a > self.n:
            self.speedA = 1/(self.transitionTimesA[(self.a-1)%self.n] - self.transitionTimesA[(self.a-self.n)%self.n])
        else:
            self.speedA = 0

        if self.b > self.n:
            self.speedB = 1/(self.transitionTimesB[(self.b-1)%self.n] - self.transitionTimesB[(self.b-self.n)%self.n])
        else:
            self.speedB = 0

        # adjust speed with PID

        self.prev_error = self.error
        self.error = self.speedA - self.speedB
        self.sum_error += self.error

        # pwmB = self.Kp * self.error + self.Ki * self.sum_error + self.Kd * (self.error - self.prev_error) + self.duty + 10

        self.get_logger().info('Speed A: %f, Speed B: %f' % (self.speedA, self.speedB))
        msg_left = Float32()
        msg_left.data = self.speedA
        self.publisher_left.publish(msg_left)

        msg_right = Float32()
        msg_right.data = self.speedB
        self.publisher_right.publish(msg_right)

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
