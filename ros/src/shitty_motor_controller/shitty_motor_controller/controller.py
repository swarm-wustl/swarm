import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist

import RPi.GPIO as GPIO

class ShittyPiComms:
    def __init__(self):
        GPIO.setwarnings(True)

        # Set up GPIO pins
        GPIO.setmode(GPIO.BCM)

        IN1 = 12
        IN2 = 16
        IN3 = 20
        IN4 = 21

        pins = [IN1, IN2, IN3, IN4]

        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)

        # Set up PWM
        self.pwm = GPIO.PWM(IN1, 100)

    def __del__(self):
        GPIO.output(IN1, 0)
        GPIO.output(IN2, 0)
        GPIO.output(IN3, 0)
        GPIO.output(IN4, 0)
        self.pwm.stop()
        GPIO.cleanup()

    def forward(self, speed):
        GPIO.output(IN1, 1)
        GPIO.output(IN2, 0)
        GPIO.output(IN3, 1)
        GPIO.output(IN4, 0)
        self.pwm.ChangeDutyCycle(speed)

    def backward(self, speed):
        GPIO.output(IN1, 0)
        GPIO.output(IN2, 1)
        GPIO.output(IN3, 0)
        GPIO.output(IN4, 1)
        self.pwm.ChangeDutyCycle(speed)

    def left(self, speed):
        GPIO.output(IN1, 0)
        GPIO.output(IN2, 1)
        GPIO.output(IN3, 1)
        GPIO.output(IN4, 0)
        self.pwm.ChangeDutyCycle(speed)

    def right(self, speed):
        GPIO.output(IN1, 1)
        GPIO.output(IN2, 0)
        GPIO.output(IN3, 0)
        GPIO.output(IN4, 1)
        self.pwm.ChangeDutyCycle(speed)

    def stop(self):
        GPIO.output(IN1, 0)
        GPIO.output(IN2, 0)
        GPIO.output(IN3, 0)
        GPIO.output(IN4, 0)
        self.pwm.stop()
        GPIO.cleanup()


class Controller(Node):

    def __init__(self):
        super().__init__('controller')
        self.subscription = self.create_subscription(
            Twist,
            '/diff_cont/cmd_vel_unstamped',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

        self.shitty_pi_comms = ShittyPiComms()

    def listener_callback(self, msg):
        x_vel = msg.linear.x
        z_ang = msg.angular.z

        if x_vel > 0:
            self.shitty_pi_comms.forward(100)
        elif x_vel < 0:
            self.shitty_pi_comms.backward(100)
        elif z_ang > 0:
            self.shitty_pi_comms.left(100)
        elif z_ang < 0:
            self.shitty_pi_comms.right(100)
        else:
            self.get_logger().info('Stop')



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
