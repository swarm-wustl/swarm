#!/usr/bin/env python


import rclpy

#from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy
import time

import geometry_msgs.msg

#from geometry_msgs.msg import Twist
#from geometry_msgs.msg import TwistStamped

import threading
import sys
if sys.platform == 'win32':
    import msvcrt
else:
    import termios
    import tty


settings = termios.tcgetattr(sys.stdin)

#1 is right
#0 is straight
#moveStatus = 1

#TwistMsg = Twist        
def saveTerminalSettings():
    if sys.platform == 'win32':
        return None
    return termios.tcgetattr(sys.stdin)


def restoreTerminalSettings(old_settings):
    if sys.platform == 'win32':
        return
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)



def vels(speed, turn):
    return "currently:\tspeed %s\tturn %s " % (speed,turn)

def main():

    settings = saveTerminalSettings();

    rclpy.init()

    node = rclpy.create_node("swarm_explore")

    


    spinner = threading.Thread(target=rclpy.spin, args=(node,))
    spinner.start()
    stamped = node.declare_parameter('stamped', False).value
    frame_id = node.declare_parameter('frame_id', '').value
    speed = 0.5
    turn = 1.0
    x = 0
    y = 0
    z = 0
    th = 0
    if stamped:
        TwistMsg = geometry_msgs.msg.TwistStamped
    else:
        TwistMsg = geometry_msgs.msg.Twist

    
    pub = node.create_publisher(TwistMsg,'cmd_vel', 10)
    twist_msg = TwistMsg();

    if stamped:
        twist = twist_msg.twist
        twist_msg.header.stamp = node.get_clock().now().to_msg()
        twist_msg.header.frame_id = frame_id
    else:
        twist = twist_msg
    moveStatus = 1
    try:
        print("starting exploration");
        print(vels(speed, turn));
        while(1):
            if moveStatus == 1:
                x = 1.0
                y = 0.0
                z = 0.0
                th = 0.0
                moveStatus = abs(moveStatus-1);
            else:
                x = 0.0
                y = 0.0
                z = 0.0
                th = 1.0
                moveStatus = abs(moveStatus-1);

            if stamped:
                twist_msg.header.stamp = node.get_clock().now().to_msg()

            twist.linear.x = x * speed
            twist.linear.y = y * speed
            twist.linear.z = z * speed
            twist.angular.x = 0.0
            twist.angular.y = 0.0
            twist.angular.z = th * turn         
            pub.publish(twist)
            time.sleep(2);
    except Exception as e:
        print(e)

    finally:
        if stamped:
            twist_msg.header.stamp = node.get_clock().now().to_msg()

        twist.linear.x = 0.0
        twist.linear.y = 0.0
        twist.linear.z = 0.0
        twist.angular.x = 0.0
        twist.angular.y = 0.0
        twist.angular.z = 0.0
        pub.publish(twist_msg)
        rclpy.shutdown()
        spinner.join()

        restoreTerminalSettings(settings)


if __name__ == '__main__':
    main()
