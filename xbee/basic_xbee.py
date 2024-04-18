from digi.xbee.devices import DigiMeshDevice
from digi.xbee.util import utils
import time

usb1 = "/dev/tty.usbserial-D38JO1QS"
usb2 = "/dev/tty.usbserial-D38JO1U8"

xbee1 = DigiMeshDevice(usb1, 9600)
xbee1.open()
xbee2 = DigiMeshDevice(usb2, 9600)
xbee2.open()

print("Setting xbee parameters...")
xbee1.set_parameter("ID", utils.hex_string_to_bytes("2015"))
xbee1.set_parameter("PL",  utils.hex_string_to_bytes("0"))
xbee1.set_parameter("DH",  utils.hex_string_to_bytes("0"))
xbee1.set_parameter("DL",  utils.hex_string_to_bytes("FFFF"))
xbee1.set_parameter("NI",  bytearray("SENDER", 'utf8'))
xbee1.set_parameter("RP",  utils.hex_string_to_bytes("5"))

xbee2.set_parameter("ID", utils.hex_string_to_bytes("2015"))
xbee2.set_parameter("PL",  utils.hex_string_to_bytes("0"))
xbee2.set_parameter("DH",  utils.hex_string_to_bytes("0"))
xbee2.set_parameter("DL",  utils.hex_string_to_bytes("FFFF"))
xbee2.set_parameter("NI",  bytearray("RECEIVER", 'utf8'))
xbee2.set_parameter("RP",  utils.hex_string_to_bytes("5"))
print("Finished setting xbee parameters")

# print("Discovering network...")
# network1 = xbee1.get_network()
# network1.start_discovery_process()
# while network1.is_discovery_running():
#     time.sleep(0.5)
# print("Finished discovering network")

while True:
    msg = input("Msg: ")
    if msg == "exit":
        break
    elif len(msg) > 0:
        xbee1.send_data_broadcast(msg)
        time.sleep(1)
        # xbee1.send_data_64(xbee2.get_64bit_addr(), msg)
        rec_msg = xbee2.read_data()
        if rec_msg is None:
            print("No message received!")
        else:
            print(rec_msg.data.decode())
    time.sleep(1)

xbee1.close()
xbee2.close()

# print(xbee1.get_node_id())

# network1 = xbee1.get_network()
# network1.start_discovery_process()
# while network1.is_discovery_running():
#     time.sleep(0.5)

# print(network1.get_devices())

# sender = network.get_device_by_node_id("SENDER")

# while True:
#     msg = input("Msg: ")
#     if msg == "exit":
#         break
#     elif len(msg) > 0:
#         device.send_data_64(sender.get_64bit_addr(), msg)

#     remote_msg = device.read_data()
#     if remote_msg is None:
#         print("No message received!")
#     else:
#         print(remote_msg.data.decode())
#     time.sleep(1)

# sender.close()