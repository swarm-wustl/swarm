from digi.xbee.devices import DigiMeshDevice
from digi.xbee.util import utils
from common.srv import XbeeOut
import random

import rclpy
from rclpy.node import Node


class XBeeService(Node):

    def __init__(self):
        super().__init__('xbee_service')
        self.srv = self.create_service(XbeeOut, 'send_xbee_msg', self.send_xbee_msg)

        usb = "/dev/ttyUSB0"
        ni = "bot_{:04}".format(random.randint(0, 9999))

        self.xbee = DigiMeshDevice(usb, 9600)
        self.xbee.open()
        self.xbee.set_parameter("ID", utils.hex_string_to_bytes("2015"))
        self.xbee.set_parameter("PL",  utils.hex_string_to_bytes("0"))
        self.xbee.set_parameter("DH",  utils.hex_string_to_bytes("0"))
        self.xbee.set_parameter("DL",  utils.hex_string_to_bytes("FFFF"))
        self.xbee.set_parameter("NI",  bytearray(ni, 'utf8'))
        self.xbee.set_parameter("RP",  utils.hex_string_to_bytes("5"))

        self.get_logger().info("XBee service has started on %s with NI: %s" % (usb, ni))

    def send_xbee_msg(self, request, response):
        response.success = True

        data = request.data
        ni = request.target_ni

        try:
            if ni == "":
                self.get_logger().info('Broadcasting data: %s' % data)
                self.xbee.send_data_broadcast(data)
            else:
                self.get_logger().info('Sending data to %s: %s' % (ni, data))
                self.get_logger().info('Not yet implemented!')
                response.success = False
                # xbee1.send_data_64(xbee2.get_64bit_addr(), msg)
        except Exception as e:
            self.get_logger().error('Error sending data: %s' % e)
            response.success = False

        return response


def main(args=None):
    rclpy.init(args=args)

    xbee_service = XBeeService()

    rclpy.spin(xbee_service)

    rclpy.shutdown()


if __name__ == '__main__':
    main()
