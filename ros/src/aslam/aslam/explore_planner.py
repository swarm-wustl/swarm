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

#from tf2_ros.transform_lister import TransformListener


import numpy as np

#from robot_navigator import BasicNavigator, NavigationResult

from math import radians, degrees

import asyncio

LOW = 0
HIGH = 1
BURGER_MAX_LIN_VEL = 0.22
BURGER_MAX_ANG_VEL = 2.84

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

        self.navigator.waitUntilNav2Active(localizer="bt_navigator")
        #dont think I need this
        #self.navigator.setInitialPose(init_pose)

    def create_task(self, task):
         print("made task")
         self.init_task = task
         self.ready = True

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
        print("map_callback!")
        self.map_meta = MapMetaData()
        self.map_header = Header()
        self.map_meta = data.info
        self.map_header = data.header
        self.map_grid_vals = np.array(data.data)
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


class GoalPlanner():

    #constructor
    def __init__(self, navigator): 
        self.nav = navigator
        self.mapH = navigator.map_meta.height #height of map
        self.mapW = navigator.map_meta.width #width of map
        self.hidden = np.zeros((self.mapW*self.mapH), dtype= bool)#place not yet been
        self.frontier = np.zeros((self.mapW*self.mapH), dtype= bool)#frontier
        self.stack = np.zeros((self.mapW*self.mapH), dtype = bool)#if its on the stack
        self.visited = np.zeros((self.mapW*self.mapH), dtype = bool) #visited
        #THIS WILL NEED TO BE CHANGED
        self.laser_range = 50
        self.goalX = 0
        self.goalY = 0
        
        self.prevGoalX = 0
        self.prevGoalY = 0

    #this is the q2e_angle helper function --> might need mods
    def q2Ang(self,w, x, y, z):
        t0 = 2.0*(w*x+y*z)
        t1 = 1.0 - 2.0*(x*x + y*y)

        xCord = math.atan2(t0, t1)
        t2 = 2.0 * (w*y-z*x)
        if(t2 > 1):
             t2 = 1.0
        elif t2 < -1.0:
             t2 = -1.0

        yCord = math.asin(t2)
        t3 = 2.0*(w*z + x*y)
        t4 = 1.0 - 2.0*(y*y+z*z)

        zCord = math.atan2(t3, t4)

        return xCord, yCord, zCord
    
    #distance helper function --> might need mods
    def distance(self, i, j):
        x1, y1 = self.getMapCords(i, j)
        x2, y2 = self.getMapCords(self.prevGoalX, self.prevGoalY)
        
        dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return dist
    
    def getMapCords(self, mapX, mapY):
        startX = int(self.mapH/2)
        startY = int(self.mapW/2)
         
        mappingX = (startX - mapX)*self.nav.map_meta.resolution
        mappingY = (startY - mapY)*self.nav.map_meta.resolution

        return mappingX, mappingY

    #get the angle of the bot
    def angle(self, s1, s2):
        equation = (s1-s2)/(1+(s1*s2))            #slope equation offset +1
        theta = math.degrees(math.atan(equation)) #from radians to degrees

        return theta

    def isHidden(self, px, py):
        xVal = self.nav.robo_position.x
        yVal = self.nav.robo_position.y
        
        xVal2, yVal2 = self.getMapCords(px, py)

        #Slope of line from position to the gap
        if yVal != yVal2:
            slope1 = (xVal2 - xVal)/(yVal2 - yVal)
        else:
            slope1 = (math.tan(math.pi/2))
        
        dist = math.sqrt(pow((xVal2-xVal),2) + pow((yVal2-yVal),2))

        x = self.nav.robo_orient.x
        y = self.nav.robo_orient.y
        z = self.nav.robo_orient.z
        w = self.nav.robo_orient.w
        #Robot orientation
        roll,pitch,yaw = self.q2Ang(x, y, z, w)
        slope2 = math.tan(yaw)
        angle = self.angle(slope1, slope2)
        #check if grid is in sensor range
        if(angle <= 90 or angle >= -90) and (dist < self.laser_range/2):
            return True
        else:
             return False
        
    #gets the nearest frontier goal
    def setFrontierGoal(self):

            nearest_fro_dist = float('Inf')
            nearest_from_x = 0
            nearest_from_y = 0
            for i in range(self.mapH):
                for j in range(self.mapW):
                    index = i*self.mapW + j

                    if self.frontier[index] == True:
                        dist = self.distance(i,j)

                        if dist < nearest_fro_dist:

                            nearest_fro_dist = dist
                            nearest_from_x = i
                            nearest_from_y = j

            self.goalX = nearest_from_x
            self.goalY = nearest_from_y		
            
    def fillStack(self):
        #rclpy.loginfo("In Stack")
        print("filling stack")
        grid_count = 0
        
        for row in range(self.mapH):
            for col in range(self.mapW):
                
                grid_count+=1
                index = col + row*self.mapW
                if self.nav.map_grid_vals[index]  != 0 or self.nav.map_grid_vals[index] != 100:
                    #check for gap
                    #if self.nav_obj.map_grid_vals[idx] == -1:
                    #   unknown += 1

                    #if the gap is not in stack
                    if self.stack[index] == False:
                            value = self.isHidden(row, col)
                            self.hidden[index] = True
                    else:
                            self.frontier[index] = True
                
                    self.stack[index] = True

        print("Total grid count: %d" %(grid_count))

    def checkPath(self, i,j):

            start = PoseStamped()
            goal = PoseStamped()

            prev_gx,prev_gy = self.getMapCords(self.prevGoalX, self.prevGoalY)

            start.header.stamp = self.nav.getClockNow()
            start.header.frame_id = "map"
            start.pose.position.x = prev_gx
            start.pose.position.y = prev_gy
            start.pose.position.z = 0.0
            start.pose.orientation.x = 0.0
            start.pose.orientation.y = 0.0
            start.pose.orientation.z = 0.0
            start.pose.orientation.w = 1.0

            gx,gy = self.getMapCords(i, j)

            goal.header.stamp = self.nav.getClockNow()
            goal.header.frame_id = "map"
            goal.pose.position.x = gx
            goal.pose.position.y = gy
            goal.pose.position.z = 0.0
            goal.pose.orientation.x = 0.0
            goal.pose.orientation.y = 0.0
            goal.pose.orientation.z = 0.0
            goal.pose.orientation.w = 1.0


            path = self.nav.navigator.getPath(start, goal)
            fail = False
            if path is None:
                 fail=True
            else:
                 if len(path.poses) == 0:
                    fail=True
            if fail:
                print("path to location:(%d,%d) not feasible" % (i, j))
                self.removeFromStack(i*self.mapW + j)
                self.removeFromStack((i+1)*self.mapW + j)
                self.removeFromStack(i*self.mapW + j+1)
                self.removeFromStack((i+1)*self.mapW + j+1)
                self.removeFromStack((i-1)*self.mapW + j)
                self.removeFromStack((i-1)*self.mapW + j-1)
                return False, None
            else:
                return True, len(path.poses)
            
    def setCurrentGoal(self):

            lower_poses_len_thresh = 10
            upper_poses_len_thresh = 30
            
            # checking if there are any goals on stack
            if np.sum(self.stack)  != 0:

                # check for hidden gaps
                if np.sum(self.hidden) > 0:

                    print("number of hidden states left: %d" %(np.sum(self.hidden)))
                    backup_i = 0
                    backup_j = 0

                    for i in range(self.mapH):
                        for j in range(self.mapW):
                            index = i*self.mapW + j

                            if self.hidden[index] == True and self.stack[index] == True:

                                # check if global path to the goal is available	
                                is_path_avail, poses_len = self.checkPath(i,j)

                                if is_path_avail == False:
                                    continue

                                if (poses_len > lower_poses_len_thresh) and (poses_len < upper_poses_len_thresh):
                                    self.goali = i
                                    self.goalj = j

                                    print("hidden goal states: %d,%d" % (self.goali, self.goalj))
                                    return True
                                else:
                                    backup_i = i
                                    backup_j = j

                    self.goalX = backup_i
                    self.goalY = backup_j

                    print("hidden goal states: %d,%d" % (self.goali, self.goalj))
                    return True

                # check for frontier gaps
                else:
                    ''' select next goal form frontier points '''
                    self.setFrontierGoal() 
                    print("frontier goal states: %d,%d" % (self.goali, self.goalj))
                    return True

            # no goals on stack
            else:
                return False

    
            
    def updateStack(self):
        for i in range(self.mapH):
            for j in range(self.mapW):
                idx = i*self.mapW+j
                if(self.nav.map_grid_vals[idx] == 0 or self.nav.map_grid_vals[idx]):
                        self.removeFromStack(idx)
                elif self.stack[idx] == True:
                        if self.hidden(i, j) == True:
                            self.hidden[idx] == True
                            self.frontier[idx] == False
                        else:
                             self.hidden[idx] == False
                             self.frontier[idx] == False
    
    ##HERHERHEHREHRHE
    def mapCoverage(self,pos_y,pos_x):

            sum_coverage = 0
            
            for y in max(-int(self.mapH/2),(pos_y - 2)),min((pos_y+2),int(self.mapH/2)) : 
                for x in max(-int(self.mapW/2),(pos_x - 2)),min((pos_x+2),int(self.mapW/2)):
                    index = y*self.mapW + x

                    if self.nav.map_grid_vals[index] == -1:
                        sum_coverage += 1

            if sum_coverage > 3: 
                return LOW
            else:
                return HIGH
    def removeFromStack(self, index):
        self.visited[index] = False
        self.hidden[index] = False
        self.frontier[index] = False
        self.stack[index] = False

    def rotate_nsec(self):
        self.nav.navigator.spin(spin_dist=1.57)


    def moveToPrevGoal(self):
            (xGoal,yGoal) = self.getMapCords(self.prevGoalX,self.prevGoalY)		
            # result, pose_len = self.check_path()
            print("backtracking to previous goal: %f ,%f" % (self.prevGoalX, self.prevGoalY))

            result = self.nav.moveToGoal(xGoal,yGoal)
    def move(self):
            ''' send goal position '''

            goalIndex = self.goalX * self.mapW + self.goalY
            (xGoal,yGoal) = self.getMapCords(self.goalX,self.goalY)

            # .loginfo("values of goalIndex in visited arraybefore move:%s" % (self.visited[goalIndex]))rospy

            result = self.nav.moveToGoal(xGoal,yGoal)

            #self.rotate_nsec()

            # update the stack list after movement
            self.updateStack()

            # goal position reached
            if result == True:

                self.prevGoalX = self.goalX
                self.prevGoalY = self.goalY

                coverage = self.mapCoverage(self.goalX,self.goalY) 
                if coverage == LOW and self.visited[goalIndex] == False:
                    # keep the goals to be explored in the end
                    print("marking visited since low coverage: (%d,%d)" %(self.goalX, self.goalY))
                    self.visited[goalIndex] = True
                    self.hidden[goalIndex] = False
                    self.frontier[goalIndex] = True
                    self.stack[goalIndex] = True
                    return
                # goal need not be explored again						
                else:
                    print("reached goal and removing from stack: (%d,%d)" %(self.goalX, self.goalY))
                    self.removeFromStack(goalIndex)
                    return

            elif self.visited[goalIndex] == False:
                # try for second time
                print("couldnt reach goal and marking for second time: (%d,%d)" %(self.goalX, self.goalY))
                self.visited[goalIndex] = True
                self.hidden[goalIndex] = True
                self.frontier[goalIndex] = False
                self.stack[goalIndex] = True

                print("goalIndex: %d, %d" % (goalIndex, (self.goalX*self.mapW + self.goalY)))
                print(self.visited[self.goalX*self.mapW + self.goalY])
                self.moveToPrevGoal()
                return
            
            else:
                # tried for two times but couldnt reach the goal remove goal from stack
                print("couldnt reach goal for second time; removing from stack: (%d,%d)" %(self.goalX, self.goalY))
                self.removeFromStack(goalIndex)
                self.removeFromStack(goalIndex+1)
                self.removeFromStack(goalIndex-1)
                self.removeFromStack(goalIndex+self.mapW)
                self.removeFromStack(goalIndex-self.mapW)
                self.moveToPrevGoal()			
                return

if __name__ == '__main__':
    try:
        navigator = MapNav()
        goal_planner = GoalPlanner(navigator)
        goal_planner.fillStack()

        while(1):
            nextGoal = goal_planner.setCurrentGoal(); 
            if nextGoal == False:
                 print("no more goal states")
                 break
            goal_planner.move()
            print("moved")
        print("exploration done")
        rclpy.spin()
    except:
        print("ended")

async def spin_once(node):
     rclpy.spin_once(node, timeout_sec=0)

async def run_node(node):
     while True:
          await spin_once(node)
          await asyncio.sleep(0.0)



async def goal_plan_task(goal_planner):
    while(1):
         
        nextGoal = goal_planner.setCurrentGoal(); 
        if nextGoal == False:
                print("no more goal states")
                break
        goal_planner.move()
        print("moved")
     
async def begin_aslam(navigator, goal_planner):
    await asyncio.gather(run_node(navigator), goal_plan_task(goal_planner))


def main(args=None):

    print("started")
    rclpy.init()
    navigator = MapNav()
    print("navigator instatiated")
    #rclpy.spin(navigator)

    ##need to have this node spin in the a different thread

    nav_loop = asyncio.get_event_loop()
    task = nav_loop.create_task(run_node(navigator))

    navigator.create_task(task)
    try:
         nav_loop.run_until_complete(task)
    except asyncio.CancelledError:
        pass
    goal_planner = GoalPlanner(navigator)
    goal_planner.fillStack()
    loop = asyncio.get_event_loop()
    
    print("map made, beginning async running aslam ")
    asyncio.run(begin_aslam(
         navigator=navigator,
         goal_planner=goal_planner
         ))
    # asyncio.run(run_node(navigator))
    #rclpy.spin(navigator)

    # goal_planner = GoalPlanner(navigator)

    # print("meow???")
    # goal_planner.fillStack()
    # print("meow???")
    # while(1):
         
    #     nextGoal = goal_planner.setCurrentGoal(); 
    #     if nextGoal == False:
    #             print("no more goal states")
    #             break
    #     goal_planner.move()
    #     print("moved")
    # print("exploration done")
    
    # try:
    #     rclpy.init()
    #     navigator = MapNav()

    #     print("meow???")
    #     goal_planner = GoalPlanner(navigator)

    #     print("meow???")
    #     goal_planner.fillStack()
    #     print("meow???")
    #     while(1):
    #         nextGoal = goal_planner.setCurrentGoal(); 
    #         if nextGoal == False:
    #              print("no more goal states")
    #              break
    #         goal_planner.move()
    #         print("moved")
    #     print("exploration done")
    #     rclpy.spin()
    # except:
    #     print("ended")