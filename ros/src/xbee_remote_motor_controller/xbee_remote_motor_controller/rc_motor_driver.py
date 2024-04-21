import RPi.GPIO as GPIO

import time
import rclpy
from rclpy.node import Node

from digi.xbee.devices import DigiMeshDevice
from digi.xbee.util import utils

class RCMotorDriver(Node):
    def __init__(self):
        super().__init__('rc_motor_driver')

        # Set up GPIO.
        GPIO.setmode(GPIO.BOARD)
        self.pins = {'in1A': 36,
                     'in2A': 38,
                     'enA': 32,
                     'in1B': 35,
                     'in2B': 37,
                     'enB': 33,
                     'servo': 40}

        for k, v in self.pins.items():
            GPIO.setup(v, GPIO.OUT)
            GPIO.output(v, GPIO.LOW)

        # PWM can take on values from 0 to 100
        self.pwmA = GPIO.PWM(self.pins['enA'], 50)
        self.pwmB = GPIO.PWM(self.pins['enB'], 50)
        self.pwmServo = GPIO.PWM(self.pins['servo'], 500)

        # Set up XBee.
        self.declare_parameter('usb', '/dev/ttyUSB0')
        usb = self.get_parameter('usb').value

        self.xbee = DigiMeshDevice(usb, 9600)
        self.xbee.open()

        apply_changes_enabled = self.xbee.is_apply_changes_enabled()
        if apply_changes_enabled:
            self.xbee.enable_apply_changes(False)

        self.xbee.set_parameter("ID", utils.hex_string_to_bytes("2015"))
        self.xbee.set_parameter("PL",  utils.hex_string_to_bytes("0"))
        self.xbee.set_parameter("DH",  utils.hex_string_to_bytes("0"))
        self.xbee.set_parameter("DL",  utils.hex_string_to_bytes("FFFF"))
        self.xbee.set_parameter("NI",  bytearray('ROBOT', 'utf8'))
        self.xbee.set_parameter("RP",  utils.hex_string_to_bytes("5"))

        self.xbee.apply_changes()
        self.xbee.write_changes()

        self.xbee.add_data_received_callback(self.update_motors)

    def __del__(self):
        GPIO.output(self.pins['in1A'], GPIO.LOW)
        GPIO.output(self.pins['in1B'], GPIO.LOW)
        GPIO.output(self.pins['in2A'], GPIO.LOW)
        GPIO.output(self.pins['in2B'], GPIO.LOW)
        self.pwmA.stop()
        self.pwmB.stop()
        GPIO.cleanup()

    def update_motors(self, message):
        data = message.data.decode('utf8')
        parse = data.split()

        if(parse[0] != 'A'):
            return

        right_motor = float(parse[1])
        left_motor = float(parse[2])
        servo = float(parse[3])

        # Update left motor outs.
        if left_motor >= 0:
            in1A_out = GPIO.HIGH
            in2A_out = GPIO.LOW
        else:
            in1A_out = GPIO.LOW
            in2A_out = GPIO.HIGH
        left_motor = 100 * (left_motor ** 2)
        
        # Update right motor outs.
        if right_motor >= 0:
            in1B_out = GPIO.HIGH
            in2B_out = GPIO.LOW
        else:
            in1B_out = GPIO.LOW
            in2B_out = GPIO.HIGH
        right_motor = 100 * (right_motor ** 4)

        # Update the pins.
        GPIO.output(self.pins['in1A'], in1A_out)
        GPIO.output(self.pins['in1B'], in1B_out)
        GPIO.output(self.pins['in2A'], in2A_out)
        GPIO.output(self.pins['in2B'], in2B_out)
        self.pwmA.start(left_motor)
        self.pwmB.start(0.8 * right_motor)
        # Currently not using servos.
        # self.pwmServo.start(13.5 + servo * -2.5)

def main(args=None):
    rclpy.init(args=args)

    rcmd = RCMotorDriver()
    
    rclpy.spin(rcmd)

    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
