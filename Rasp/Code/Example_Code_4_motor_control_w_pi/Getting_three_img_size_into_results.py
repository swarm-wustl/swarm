# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 11:42:35 2023

@author: Bruce Wayne AKA Edgar and Nicolas Hernandez 
"""
# program for getting the size of images and saving them under "results.txt" 

import cv2 


with open('results.txt', 'w') as pp:
	img1 = cv2.imread('Original.jpg')
	height, width, _ = img1.shape
	pp.write(str(height) + ',' + str(width)  + ' \n') 
	img2 = cv2.imread('Original_resized.jpg')
	height, width, _ = img2.shape 
	pp.write(str(height) + ',' + str(width)  + ' \n')
	img3 = cv2.imread('Original_thmb.jpg') 
	height, width, _ = img2.shape
	pp.write(str(height) + ',' + str(width)  + ' \n')
 
