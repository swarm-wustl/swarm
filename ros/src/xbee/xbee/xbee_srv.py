from digi.xbee.devices import DigiMeshDevice
from digi.xbee.util import utils
from common.srv import XbeeOut
import random
import json

from std_msgs.msg import String

import rclpy
from rclpy.node import Node

# MAX_DATA_SIZE = 72
MAX_DATA_SIZE = 42 # answer to the ultimate question of life, the universe, and everything

class XBeeService(Node):

    def __init__(self):
        super().__init__('xbee_service')
        self.srv = self.create_service(XbeeOut, 'send_xbee_msg', self.send_xbee_msg)
        self.publisher_ = self.create_publisher(String, 'xbee_in', 10)

        self.declare_parameter('usb', '/dev/ttyUSB0')
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

        self.get_logger().info("XBee service has started on %s with NI: %s" % (usb, ni))

        self.data_incoming_stream = []

    def send_xbee_msg(self, request, response):
        response.success = True

        datas = [request.data]
        ni = request.target_ni

        # split data into chunks of MAX_DATA_SIZE
        if len(datas[0]) > MAX_DATA_SIZE:
            datas = [datas[0][i:i+MAX_DATA_SIZE] for i in range(0, len(datas[0]), MAX_DATA_SIZE)]
        print(datas)

        try:
            # if ni == "":
            for i, data in enumerate(datas):
                formatted_data = self.format_data(data, i, i == len(datas) - 1)
                self.get_logger().info('Broadcasting data: %s' % data)
                self.xbee.send_data_broadcast(formatted_data)
            # else:
            #     for i, data in enumerate(datas):
            #         self.get_logger().info('Sending data to %s: %s' % (ni, data))
            #         self.get_logger().info('Not yet implemented!')
            #         response.success = False
            #         # xbee1.send_data_64(xbee2.get_64bit_addr(), msg)
        except Exception as e:
            self.get_logger().error('Error sending data: %s' % e)
            response.success = False

        return response
    
    def format_data(self, data, n, last):
        return json.dumps({
            "n": n, # packet number
            "l": 1 if last else 0, # 1 if last packet, 0 otherwise
            "d": data,
        })

    def xbee_received(self, xbee_message):
        address = xbee_message.remote_device.get_64bit_addr()
        data = xbee_message.data.decode("utf8")
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            self.get_logger().error('Error decoding data: %s' % e)
            return

        if data["n"] == 0:
            self.data_incoming_stream = []

        self.data_incoming_stream.append(data)

        if data["l"] == 1:
            concat = ""
            self.data_incoming_stream.sort(key=lambda x: x["n"])

            for i, d in enumerate(self.data_incoming_stream):
                if i != d["n"]:
                    self.get_logger().error('Data packet out of order: %s' % d)
                    self.data_incoming_stream = []
                    return
                concat += d["d"]

            self.get_logger().info('Received data from %s: %s' % (address, concat))
            msg = String()
            msg.data = concat
            self.publisher_.publish(msg)
            self.data_incoming_stream = []

def main(args=None):
    rclpy.init(args=args)

    xbee_service = XBeeService()

    rclpy.spin(xbee_service)

    rclpy.shutdown()


if __name__ == '__main__':
    main()
