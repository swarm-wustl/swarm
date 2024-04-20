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
            GPIO.output(v, 0)

        # PWM can take on values from 0 to 100
        self.pwmA = GPIO.PWM(self.pins['enA'], 50)
        self.pwmB = GPIO.PWM(self.pins['enB'], 50)
        self.pwmServo = GPIO.PWM(self.pins['servo'], 50)

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
        for k, v in self.pins.items():
            GPIO.output(v, 0)
        self.pwmA.stop()
        self.pwnB.stop()
        self.pwmServo.stop()

    def update_motors(self, message):
        data = message.data.decode('utf8')
        print(data)

def main(args=None):
    rclpy.init(args=args)

    rcmd = RCMotorDriver()
    
    rclpy.spin(rcmd)

    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
