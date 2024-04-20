import sys
import time

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Joy

from digi.xbee.devices import DigiMeshDevice
from digi.xbee.util import utils
from digi.xbee.devices import RemoteXBeeDevice

class RemoteController(Node):

    def __init__(self):
        super().__init__('remote_controller')
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
        self.xbee.set_parameter("NI",  bytearray('CONTROL', 'utf8'))
        self.xbee.set_parameter("RP",  utils.hex_string_to_bytes("5"))

        self.xbee.apply_changes()
        self.xbee.write_changes()

        self.subscription = self.create_subscription(
            Joy,
            '/joy',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

        self.xnet = self.xbee.get_network()
        self.remote = self.xnet.discover_device("ROBOT")

    def listener_callback(self, msg):
        left_motor = msg.axes[1]
        right_motor = msg.axes[4]
        servo = (msg.axes[5] - 1) / (-2)

        self.xbee.send_data(self.remote, "A {} {} {}".format(left_motor, right_motor, servo))

def main(args=None):
    rclpy.init(args=args)

    rc = RemoteController()

    rclpy.spin(rc)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    rc.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
