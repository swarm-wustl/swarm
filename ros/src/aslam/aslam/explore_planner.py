import numpy as np 
from map_nav import *
import os
import math
import time
import random

from map_nav import *

import rclpy
import rclpy.exceptions
import rclpy.exceptions
import rclpy.logging
from rclpy.node import Node 
from rclpy.action import ActionClient

import sys
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult


LOW = 0
HIGH = 1
BURGER_MAX_LIN_VEL = 0.22
BURGER_MAX_ANG_VEL = 2.84


class GoalPlanner():

    #constructor
    def __init__(self, navigator): 
        self.nav = navigator
        self.mapH = navigator.meta_map.height #height of map
        self.mapW = navigator.meta_map.width #width of map
        self.hidden = np.zeros((self.mapW*self.mapH), dtype= bool)#place not yet been
        self.frontier = np.zeros((self.mapW*self.mapH), dtype= bool)#frontier
        self.stack = np.zeros((self.mapW*self.mapH), dtype = bool)#if its on the stack
        self.visited = np.zeros((self.mapW*self.mapH), dtype = bool) #visited
        #THIS WILL NEED TO BE CHANGED
        self.laser_range = rclpy.get_param("/turtlebot3_slam_gmapping/maxUrange") 
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

        zCord = math.atan(t3, t4)

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
        
        dist = math.sqrt((xVal2-xVal).pow(2) + (yVal2-yVal).pow(2))

        optX = self.nav.robo_orient.optX
        optY = self.nav.robo_orient.optY
        optZ = self.nav.robo_orient.optZ
        optW = self.nav.robo_orient.optW
        #Robot orientation
        roll,pitch,yaw = self.q2Ang(optX, optY, optZ, optW)
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
            srv = GetPlan()

            start = PoseStamped()
            goal = PoseStamped()

            prev_gx,prev_gy = self.getMapCords(self.prevGoalX, self.prevGoalY)

            start.header.seq = 0
            start.header.stamp = self.nav.getClockNow()
            start.header.frame_id = "map"
            start.pose.position.x = prev_gx
            start.pose.position.y = prev_gy
            start.pose.position.z = 0.0
            start.pose.orientation.x = 0
            start.pose.orientation.y = 0
            start.pose.orientation.z = 0
            start.pose.orientation.w = 1

            gx,gy = self.getMapCords(i, j)

            goal.header.seq = 0
            goal.header.stamp = self.nav.getClockNow()
            goal.header.frame_id = "map"
            goal.pose.position.x = gx
            goal.pose.position.y = gy
            goal.pose.position.z = 0.0
            goal.pose.orientation.x = 0.0
            goal.pose.orientation.y = 0.0
            goal.pose.orientation.z = 0.0
            goal.pose.orientation.w = 1.0


            plan = self.nav.navigator.getPath(start, goal)

            if len(plan.plan.poses) == 0:
                print("path to location:(%d,%d) not feasible" % (i, j))
                self.removeFromStack(i*self.mapW + j)
                self.removeFromStack((i+1)*self.mapW + j)
                self.removeFromStack(i*self.mapW + j+1)
                self.removeFromStack((i+1)*self.mapW + j+1)
                self.removeFromStack((i-1)*self.mapW + j)
                self.removeFromStack((i-1)*self.mapW + j-1)
                return False, None
            else:
                return True, len(plan.plan.poses)
            
    def setCurrentGoal(self):

            lower_poses_len_thresh = 10
            upper_poses_len_thresh = 30
            
            # checking if there are any goals on stack
            if np.sum(self.on_stack)  != 0:

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

            self.rotate_nsec()

            # update the on_stack list after movement
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