# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 17:47:59 2023

@author: Bruce Wayne AKA Edgar and Nicolas Hernandez 
"""

import math as m 

def origin_calcualtion(img, pixelY, pixelX):
    
    # Calculate the variables needed for the equation. 
    
    # Get the original dimensions of the image
    height_total, width_total, _ = img.shape
    
    # divide height by two to get the center of the image, the reference point
    half_w = height_total/2 
    
    # calculate the opposite side of the angle
    opposite_side = height_total - pixelY 
    
    # calculate the adjacent side
    adjacent_side = abs(half_w - pixelX) 
    
    # calculate angle
    theta = m.atan(opposite_side/adjacent_side) 
    
    # Angle variable for calculation
    angle = 0
    
    # Check which side of the image the angle is in
    if(adjacent_side > half_w):  # if grater than half, pixel is to the right of center
        angle = 90 - theta
    else: # else it is to the left of the center. 
        angle = theta - 90 
    
    return angle


    
    

    
