import numpy as np 
import os
import math
import time
import random

import rclpy
import rclpy.exceptions
import rclpy.exceptions
import rclpy.executors
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

import rclpy.subscription
from tf2_msgs.msg import TFMessage

from nav_msgs.srv import *
from std_msgs.msg import *
#from nav2_msgs.msg import CostMap

from rclpy.duration import Duration

from geometry_msgs.msg import PoseStamped

class MapNav(Node):

    def __init__(self):
        
        # FIX A SHIT TON OF ERRORS
        #here create the actual node inheriting from the node class
        super().__init__("swarm_aslam")

        self.create_subscription(OccupancyGrid, 
                                 "map", 
                                 self.map_callback,
                                 10)
        self.create_subscription(Costmap, 
                                 "global_cosmap/costmap",
                                   self.global_costmap_callback,
                                    10 )
        self.create_subscription(TFMessage, 
                                 "tf", 
                                 self.pose_callback,
                                  10 )
        #self.rob_pub = self.create_publisher("cmd_vel",Twist,queue_size=10)
        #action server for nav2
        #self.ac = ActionClient(,"move_base"); 

        ## this is to ensure that the map is made first before running the goal planner
        self.map_made = False
        self.robot_pos_made = False
        self.ready = False
        self.navigator = BasicNavigator()

        initial_pose = PoseStamped()
        initial_pose.header.frame_id = 'map'
        initial_pose.header.stamp = self.navigator.get_clock().now().to_msg()
        initial_pose.pose.position.x = 0.0
        initial_pose.pose.position.y = 0.0
        initial_pose.pose.orientation.z = 0.0
        initial_pose.pose.orientation.w = 1.0
        self.navigator.setInitialPose(initial_pose)
        self.fill_call_made = False
        self.navigator.waitUntilNav2Active(localizer="bt_navigator")
        
        
        #dont think I need this
        #self.navigator.setInitialPose(init_pose)

    def create_task(self, task):
         print("made task")
         self.init_task = task
         self.ready = True

    ## ONE THING IS MAKE ASLAM ACCOUNT FOR THE MAP GETTING BIGGER
    def add_fill_call_back(self, call_back):
         self.fill_call_made = True
         self.fill_call_back = call_back

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
        if self.fill_call_made:
             print("updated")
             self.fill_call_back()
        if not self.map_made and not self.robot_pos_made:
                self.map_made = True
        elif not self.map_made:
            self.map_made = True
            self.init_task.cancel()

    def global_costmap_callback(self, data):
        self.global_costmap_meta = MapMetaData()
        self.global_costmap_header = Header()
        self.global_costmap_meta = data.info
        self.global_costmap_header = data.header
        self.global_costmap_probs = np.array(data.data)

    def pose_callback(self, data):

        #print(data)
        #print(data.transforms[-1].header.frame_id)
        if data.transforms[-1].header.frame_id == "map":
            if data.transforms[-1].child_frame_id == "odom":
                
                #print("MEOW MOVE ")
                self.robo_position = Point()  #figure out this function
                self.robo_position.x = data.transforms[-1].transform.translation.x
                self.robo_position.y = data.transforms[-1].transform.translation.y

                self.robo_orient = Quaternion() #figure out this function
                #check hidden function in explore_planner
                self.robo_orient.x = data.transforms[-1].transform.rotation.x
                self.robo_orient.y = data.transforms[-1].transform.rotation.y
                self.robo_orient.z = data.transforms[-1].transform.rotation.z
                self.robo_orient.w = data.transforms[-1].transform.rotation.w
                if not self.map_made and not self.robot_pos_made:
                    self.robot_pos_made = True
                elif not self.robot_pos_made:
                    self.robot_pos_made = True
                    self.init_task.cancel()

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
            if feedback.navigation_time.sec > 600:
                self.navigator.cancelTask()
        #self.navigator.lifecycleShutdown()
        
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

