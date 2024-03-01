#!/usr/bin/env python

import rclpy
from rclpy.node import Node 
from rclpy.action import ActionClient

import sys
from nav2_simple_commander.robot_navigator import BasicNavigator

from nav_msgs.msg import OccupancyGrid
#from nav2_msgs.msg import CostMap

from rclpy.duration import Duration

from geometry_msgs.msg import PoseStamped

#from tf2_ros.transform_lister import TransformListener


import numpy as np

#from robot_navigator import BasicNavigator, NavigationResult

from math import radians, degrees


if sys.platform == 'win32':
    import msvcrt
else:
    import termios
    import tty

class MapNav(Node):

    def __init__(self):
        
        #here create the actual node inheriting from the node class
        super().__init__("swarm_aslam");
 

        #self.create_subscription(OccupancyGrid, "map", self.map_callback);
        #self.create_subscription(CostMap, "move_base/global_cosmap/costmap", self.cost_map_callback )
        
        #self.rob_pub = self.create_publisher("cmd_vel",Twist,queue_size=10)

        #action server for nav2

        #self.ac = ActionClient(,"move_base"); 
        
        self.navigator = BasicNavigator()


    def test_move(self):
        goalPose = PoseStamped()
        goalPose.header.frame_id = 'map'
        goalPose.header.stamp = self.navigator.get_clock().now().to_msg()
        goalPose.pose.position.x = 10.0
        goalPose.pose.position.y = -2.0
        goalPose.pose.position.z = 0.0
        goalPose.pose.orientation.x = 0.0
        goalPose.pose.orientation.y = 0.0
        goalPose.pose.orientation.z = 0.0
        goalPose.pose.orientation.w = 0.0

        self.navigator.goToPose(goalPose);
        print("move sent!")
        


    def map_callback(self, data):
        self.map_meta = MapMetaData()
        self.map_header = Header()
        self.map_meta = data.info
        self.map_header = data.header
        self.map_grid_vals = np.array(data.data)

    def global_costmap_callback(self, data):
        self.global_costmap_meta = MapMetaData()
        self.global_costmap_header = Header()
        self.global_costmap_meta = data.info
        self.global_costmap_header = data.header
        self.global_costmap_probs = np.array(data.data)

def main():
    
    rclpy.init()

    mapNode = MapNav();

    mapNode.test_move(); 

if __name__ == "__main__":
    mapNode = MapNav();

    mapNode.test_move();
