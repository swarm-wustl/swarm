#!/usr/bin/env python

## DEPRECATED FOR NOW


import rclpy
import rclpy.logging
from rclpy.node import Node 
from rclpy.action import ActionClient

import sys
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

from actionlib_msgs.msg import *
from geometry_msgs.msg import *
#these import the classes for cost map, Occupancy Grid
from nav_msgs.msg import *
from nav2_msgs.msg import *

from tf2_msgs.msg import TFMessage

from nav_msgs.srv import *
from std_msgs.msg import *
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
        super().__init__("swarm_aslam")
        self.create_subscription(OccupancyGrid, 
                                 "map", 
                                 self.map_callback)
        self.create_subscription(Costmap, 
                                 "global_cosmap/costmap",
                                   self.cost_map_callback )
        self.create_subscription(TFMessage, 
                                 "tf", 
                                 self.pose_callback )
        #self.rob_pub = self.create_publisher("cmd_vel",Twist,queue_size=10)
        #action server for nav2
        #self.ac = ActionClient(,"move_base"); 
        self.navigator = BasicNavigator()

        initial_pose = PoseStamped()
        initial_pose.header.frame_id = 'map'
        initial_pose.header.stamp = self.navigator.get_clock().now().to_msg()
        initial_pose.pose.position.x = 0
        initial_pose.pose.position.y = 0
        initial_pose.pose.orientation.z = 0
        initial_pose.pose.orientation.w = 1.0
        self.navigator.setInitialPose(initial_pose)

        self.navigator.waitUntilNav2Active()
        #dont think I need this
        #self.navigator.setInitialPose(init_pose)

    def test_move(self):
        print(TaskResult)
        goalPose = PoseStamped()
        goalPose.header.frame_id = 'map'
        goalPose.header.stamp = self.navigator.get_clock().now().to_msg()
        goalPose.pose.position.x = 100.0
        goalPose.pose.position.y = -2.0
        goalPose.pose.position.z = 0.0
        goalPose.pose.orientation.x = 0.0
        goalPose.pose.orientation.y = 0.0
        goalPose.pose.orientation.z = 0.0
        goalPose.pose.orientation.w = 0.0

        self.navigator.goToPose(goalPose)
        print("move sent!")
        while not self.navigator.isTaskComplete():
            print("MEOW")
        self.navigator.lifecycleShutdown()


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

    def pose_callback(self, data):
        if data.transforms[-1].header.frame_id == "map":
            if data.transforms[-1].header.frame_id == "odom":
                self.roboPos = Point()  #figure out this function
                self.roboPos.optX = data.transforms[-1].transform.translation.optX
                self.roboPos.optY = data.transforms[-1].transform.translation.optY

                self.robo_orient = Quaternion() #figure out this function
                #check hidden function in explore_planner
                self.robo_orient.optX = data.transforms[-1].transform.rotation.optX
                self.robo_orient.optY = data.transforms[-1].transform.rotation.optY
                self.robo_orient.optZ = data.transforms[-1].transform.rotation.optZ
                self.robo_orient.optW = data.transforms[-1].transform.rotation.optW

    def track_local(self, path):
            self.prev_init_local_pose = path.poses[0].pose
    def track_global(self, path):
            pass
    
    def getClockNow(self):
        return self.navigator.get_clock().now().to_msg()

    def moveToGoal(self,xGoal,yGoal):

        #stamp and header info
        goalPose = PoseStamped()
        goalPose.header.frame_id = 'map'
        goalPose.header.stamp = self.navigator.get_clock().now().to_msg()
        
        #set position to inputted xGoal
        goalPose.pose.position.x = xGoal
        goalPose.pose.position.y = yGoal
        goalPose.pose.position.z = 0.0
        goalPose.pose.orientation.x = 0.0
        goalPose.pose.orientation.y = 0.0
        goalPose.pose.orientation.z = 0.0
        goalPose.pose.orientation.w = 1.0

        #move to goal Pose
        self.navigator.goToPose(goalPose)

        #get there until task is complete, meaning the robot goal ended (which could be succeed for giving up)
        
        #or end this attempt if it takes to long

        while not self.navigator.isTaskComplete():
            #if the goToPose takes longer than 600 seconds give up
            feedback = self.navigator.getFeedback()
            if feedback.navigation_duration > 600:
                self.navigator.cancelTask()
        self.navigator.lifecycleShutdown()
        
        result = self.navigator.getResult()
        
        #if robot made it return true, else false meaning the robot failed
        if result == TaskResult.SUCCEEDED:
            print('Goal succeeded!')
            return True
        elif result == TaskResult.CANCELED:
            print('Goal was canceled!')
        elif result == TaskResult.FAILED:
            print('Goal failed!')
        return False

def test(args=None):

    rclpy.init(args=args)
    mapNode = MapNav()

    mapNode.test_move()

def main(args=None):
    rclpy.init(args=args)
    mapNode = MapNav()

##technically this should never be called main unless for testing
if __name__ == "__main__":
    main()