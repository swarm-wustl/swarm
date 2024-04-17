from digi.xbee.devices import DigiMeshDevice
import time

usb1 = "/dev/tty.usbserial-D38JO1QS"
usb2 = "/dev/tty.usbserial-D38JO1U8"

xbee1 = DigiMeshDevice(usb1, 9600)
xbee1.set_parameter("AP",  1)
xbee1.open()

xbee2 = DigiMeshDevice(usb2, 9600)
xbee2.open()

xbee1.close()
xbee2.close()

# xbee.set_parameter("NI",  bytearray("Yoda", 'utf8'))

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
