import numpy as np 
from map_nav import *
import os
import math
import time
import random
import rclpy

class plan():

    #constructor
    def __init__(self, obj_swarm): 
        self.obj_swarm = obj_swarm
        self.mapH = obj_swarm.meta_map.height #height of map
        self.mapW = obj_swarm.meta_map.width #width of map
        self.unknown = np.zeros((self.mapW*self.mapH), dtype= bool)#place not yet been
        self.inFront = np.zeros((self.mapW*self.mapH), dtype= bool)#frontier
        self.stack = np.zeros((self.mapW*self.mapH), dtype = bool)#if its on the stack
        self.known = np.zeros((self.mapW*self.mapH), dtype = bool) #visited
        self.laser_range = rclpy.get_param("/turtlebot3_slam_gmapping/maxUrange") #no idea what this does lowkey lol
        self.newGoalH = 0
        self.newGoalC = 0
        
        self.prevGoalH = 0
        self.prevGoalW = 0

    #this is the q2e_angle helper function --> might need mods
    def q2Ang(self,w, x, y, z):
        t0 = 2.0(w*x+y*z)
        t1 = 1.0 - 2.0(x*x + y*y)

        xCord = math.atan2(t0, t1)
        t2 = 2.0 * (w*y-z*x)
        if(t2 > 1):
             t2 = 1.0
        elif t2 < -1.0:
             t2 = -1.0

        yCord = math.asin(t2)
        t3 = 2.0(w*z + x*y)
        t4 = 1.0 - 2.0(y*y+z*z)

        zCord = math.atan(t3, t4)

        return xCord, yCord, zCord
    
    #distance helper function --> might need mods
    def distance(self, i, j):
        x1, y1 = self.mapCords(i, j)
        x2, y2 = self.mapCords(self.prevGoalH, self.prevGoalW)
        
        dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return dist
    
    def mapCords(self, mapX, mapY):
        startX = int(self.mapH/2)
        startY = int(self.mapW/2)
         
        mappingX = (startX - mapX)*self.obj_swarm.map_meta.resolution
        mappingY = (startY - mapY)*self.obj_swarm.map_meta.resolution

        return mappingX, mappingY

    #get the angle of the bot
    def angle(self, s1, s2):
        equation = (s1-s2)/(1+(s1*s2))            #slope equation offset +1
        theta = math.degrees(math.atan(equation)) #from radians to degrees

        return theta

    def hidden(self, px, py):
        xVal = self.obj_swarm.robo_position.x
        yVal = self.obj_swarm.robo_position.y
        
        xVal2, yVal2 = self.mapCords(px, py)

        #Slope of line from position to the gap
        if yVal != yVal2:
            slope1 = (xVal2 - xVal)/(yVal2 - yVal)
        else:
            slope1 = (math.tan(math.pi/2))
        
        theDist = math.sqrt((xVal2-xVal).pow(2) + (yVal2-yVal).pow(2))

        optX = self.obj_swarm.robo_orient.optX
        optY = self.obj_swarm.robo_orient.optY
        optZ = self.obj_swarm.robo_orient.optZ
        optW = self.obj_swarm.robo_orient.optW
        #Robot orientation
        roll,pitch,yaw = self.q2Ang(optX, optY, optZ, optW)
        slope2 = math.tan(yaw)
        theta = self.angle(slope1, slope2)
        #check if grid is in sensor range
        if(theta <= 90 or theta >= -90) and (theDist < self.laser_range/2):
            return True
        else:
             return False
        
    def fullStack(self):
        #rclpy.loginfo("In Stack")
        grid_count = 0
        
        for row in range(self.mapH):
            for col in range(self.mapW):
                
                grid_count+=1
                idx = col + row*self.mapW
                if self.obj_swarm.map_grid_vals[idx] == -1:
                    #check for gap
                    #if self.nav_obj.map_grid_vals[idx] == -1:
                    #   unknown += 1

                    #if the gap is not in stack
                    if self.on_stack[idx] == False:
                            value = self.ishidden(row, col)
                            self.hidden[idx] = True
                    else:
                            self.frontier[idx] = True
                
                    self.on_stack[idx] = True

        #rclpy.loginfo("Total grid count: %d" %(grid_count))
    
    def updateStack(self):
        for i in range(self.mapH):
            for j in range(self.mapW):
                idx = i*self.mapW+j
                if(self.obj_swarm.map_grid_vals[idx] == 0 or self.obj_swarm.map_grid_vals[idx]):
                        self.remove_stack(idx)
                elif self.on_stack[idx] == True:
                        if self.hidden(i, j) == True:
                            self.hidden[idx] == True
                            self.frontOf[idx] == False
                        else:
                             self.hidden[idx] == False
                             self.frontOf[idx] == False

    def remove_stack(self, index):
        self.seen[index] = False
        self.hidden[index] = False
        self.frontOf[index] = False
        self.on_stack[index] = False

