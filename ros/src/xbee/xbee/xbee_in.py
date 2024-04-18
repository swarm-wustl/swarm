import rclpy
from rclpy.node import Node
from digi.xbee.devices import DigiMeshDevice
from digi.xbee.util import utils
import random

from std_msgs.msg import String


class XBeeReceiver(Node):

    def __init__(self):
        super().__init__('xbee_receiver')
        self.publisher_ = self.create_publisher(String, 'xbee_in', 10)
        timer_period = 2  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        self.declare_parameter('usb')
        usb = self.get_parameter('usb').value
        ni = "bot_{:04}".format(random.randint(0, 9999))

        self.xbee = DigiMeshDevice(usb, 9600)
        self.xbee.open()
        self.xbee.set_parameter("ID", utils.hex_string_to_bytes("2015"))
        self.xbee.set_parameter("PL",  utils.hex_string_to_bytes("0"))
        self.xbee.set_parameter("DH",  utils.hex_string_to_bytes("0"))
        self.xbee.set_parameter("DL",  utils.hex_string_to_bytes("FFFF"))
        self.xbee.set_parameter("NI",  bytearray(ni, 'utf8'))
        self.xbee.set_parameter("RP",  utils.hex_string_to_bytes("5"))

        self.xbee.add_data_received_callback(self.xbee_received)

    def xbee_received(self, xbee_message):
        address = xbee_message.remote_device.get_64bit_addr()
        data = xbee_message.data.decode("utf8")
        self.get_logger().info('Received data from %s: %s' % (address, data))
        msg = String()
        msg.data = data
        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
