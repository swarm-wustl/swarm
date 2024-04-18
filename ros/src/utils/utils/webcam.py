import rclpy
from rclpy.node import Node
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

class ImagePublisher(Node):
    def __init__(self):
        super().__init__("image_publisher")
        self.bridge = CvBridge()
        self.cap = cv2.VideoCapture(0)
        self.pub = self.create_publisher(Image, "/camera/image_raw", 10)

    def run(self):
        try:
            while True:
                try:
                    r, frame = self.cap.read()
                    if not r:
                        return
                    self.pub.publish(self.bridge.cv2_to_imgmsg(frame, "bgr8"))

                except CvBridgeError as e:
                    print(e)
        except KeyboardInterrupt:
            self.cap.release()

def main(args=None):
    rclpy.init(args=args)

    ip = ImagePublisher()
    print("Publishing...")
    ip.run()

    ip.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

