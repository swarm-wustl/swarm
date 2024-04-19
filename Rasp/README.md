README RASPBERRY PI


Host Name: swarmpi-one

User Name: swarmpi-one 

Instructions to SSH: 

ssh swarmpi-one@swarmpi-one 
username: swarmpi-one
password: 1234 

To Clone Github:

$ cd .ssh

$ ssh-keygen -t ed25519 -C "your_email@wustl.edu"

Go to github settings and add ssh key. Copy paste the .pub key in.

$ cd ..

$ git clone git@github.com:swarm-wustl/swarm.git

% Controlling GPIO pins with C++
PiGPIO Install Instructions: https://abyz.me.uk/rpi/pigpio/download.html
Compile code using: g++ -Wall -pthread -o programName programName.cpp -lpigpio -lrt


% HELPUL LINKS: 
______________________________________________________________________________
% Raspberry Pi related hardware links: 
https://docs.google.com/document/d/1s1zL08Ik6HmopOrnkhIOqFlx5rBDgq-PfivWDXDRpwo/edit

% pigpio information:
https://abyz.me.uk/rpi/pigpio/index.html

% H-bride (Motor Driver) Conneciton to PI: 
https://sharad-rawat.medium.com/interfacing-l298n-h-bridge-motor-driver-with-raspberry-pi-7fd5cb3fa8e3

% Type of H-Bridge (Motor Driver) Model:
https://www.amazon.com/HiLetgo-Controller-Stepper-H-Bridge-Mega2560/dp/B07BK1QL5T/ref=cm_cr_arp_d_product_top?ie=UTF8

% Type of Motor: 
https://www.robotshop.com/products/6v-1001-micro-metal-gearmotor-w-encoder-cable-150rpm


