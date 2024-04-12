# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 18:12:22 2023

@author: Bruce Wayne AKA Edgar Sarceno and Nicolas Hernandez 
"""


# Program1.py 

import cv2


# Load the input image
#img = cv2.imread('monarch.jpg')
img=cv2.imread(input(''))
cv2.imwrite("Original.jpg", img)

def resize_image_same_ratio(img): 

    
    # Get the original dimensions of the image
    height, width, _ = img.shape
    
    # Get user input for desired width
    new_width = int(input("Enter desired width: "))
    
    # Calculate the scaling factor to maintain aspect ratio
    scale_factor = new_width / width
    new_height = int(height * scale_factor)
    
    # Resize the image
    resized_img = cv2.resize(img, (new_width, new_height), interpolation = cv2.INTER_AREA)
    
    # Save the resized image
    cv2.imwrite("Original_resized.jpg", resized_img)
    
    print(f"Image resized to {new_width} width and saved as resized.jpg")


resize_image_same_ratio(img)
