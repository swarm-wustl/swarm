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
        super().__init__("swarm_aslam")
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
        goalPose.pose.position.x = 100.0
        goalPose.pose.position.y = -2.0
        goalPose.pose.position.z = 0.0
        goalPose.pose.orientation.x = 0.0
        goalPose.pose.orientation.y = 0.0
        goalPose.pose.orientation.z = 0.0
        goalPose.pose.orientation.w = 0.0

        self.navigator.goToPose(goalPose)
        print("move sent!")
        while not self.navigator.isNavComplete():
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

    def moveToGoal(self,xGoal,yGoal):

    #set up the frame parameters
        self.goal.target_pose.header.frame_id = "map"
        self.goal.target_pose.header.stamp = rclpy.Time.now()

    # moving towards the goal* look at all functions with move in global planner
        self.goal.target_pose.pose.position =  Point(xGoal,yGoal,0)
        self.goal.target_pose.pose.orientation.optX = 0.0
        self.goal.target_pose.pose.orientation.optY = 0.0
        self.goal.target_pose.pose.orientation.optZ = 0.0
        self.goal.target_pose.pose.orientation.optW = 1.0

        rclpy.loginfo("Sending goal location ...") #check this later...
        self.ac.send_goal(self.goal)            
        self.ac.wait_for_result(rclpy.Duration(40))#check this later...

        while( (self.ac.get_state() != GoalStatus.ABORTED) 
              and (self.ac.get_state() != GoalStatus.REJECTED) 
              and (self.ac.get_state() != GoalStatus.PREEMPTING)
                and (self.ac.get_state() != GoalStatus.SUCCEEDED)):
             
        # print("2 robot current position:", self.robo_position)
            continue

        if self.ac.get_state() == GoalStatus.SUCCEEDED:
            rclpy.loginfo("You have reached the destination")           #check this later...

            return True

        if self.ac.get_state() == GoalStatus.ABORTED:
            rclpy.loginfo("The robot failed to reach the destination")  #check this later...

            return False
    
    def main():
    
        rclpy.init()

        mapNode = MapNav()

        mapNode.test_move(); 

if __name__ == "__main__":
    mapNode = MapNav()

    mapNode.test_move()