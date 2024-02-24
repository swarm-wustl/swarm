import numpy as np 
from map_nav import *
import os
import math
import time
import random


class plan():

    #constructor
    def __init__(self, obj_swarm): 
        self.obj_swarm = obj_swarm
        self.mapRow = mapRow.meta_map.height #height of map
        self.mapCol = mapCol.meta_map.width #width of map
        self.unknown = np.zeros((self.mapCol*self.mapRow), dtype= bool)
        self.inFront = np.zeros((self.mapCol*self.mapRow), dtype= bool)
        self.stack = np.zeros((self.mapCol*self.mapRow), dtype = bool)
        self.known = np.zeros((self.mapCol*self.mapRow), dtype = bool)
        self.newGoalRow = 0
        self.newGoalCol = 0
        
        self.prevGoalRow = 0
        self.prevGoalCol = 0

    def hiddem(self, px, py):
        xVal = self.obj_swarm.robo_position.x
        yVal = self.obj_swarm.robo_position.y
        

    def fullStack():
        
        rospy.loginfo("In Stack")
        grid_count = 0
        
        for row in range(self.mapRow):
            for col in range(self.mapCol):
                
                grid_count+=1
                idx = col + row*self.mapCol

                #check for gap
                #if self.nav_obj.map_grid_vals[idx] == -1:
                #   unknown += 1

                #if the gap is not in stack

