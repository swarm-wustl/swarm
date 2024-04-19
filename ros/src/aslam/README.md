# ASLAM

Aslam stands for active-slam, in which uses slam to actively make decisions

AT CURRENT ITERATION this version uses LIDAR slam and is still WIP 

## setup

install these packages

- sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup ros-humble-twist-mux ros-humble-slam-toolbox ros-humble-gazebo-ros2-control

### trouble shoot errors (queue full)

You must have ros-humble-gazebo-ros2-control set up you'll get a queue is full error when running nav2. TBH idk why there is NOTHING ONLINE ABOUT THAT like bruh.

## running

run these commands in /ros directory before running ASLAM

### apartment map and running gazebo

ros2 launch swarm_bot launch_sim.launch.py world:=./src/swarm_bot/worlds/apartmentswag.world

### maze map and running gazebo

ros2 launch swarm_bot launch_sim.launch.py world:=./src/swarm_bot/worlds/maze_swarm_map.world

### Async SLam

ros2 launch slam_toolbox online_async_launch.py params_file:=./src/swarm_bot/config/mapper_params_online_async.yaml use_sim_time:=True

### nav2 

ros2 launch swarm_bot navigation_launch.py params_file:=./src/swarm_bot/config/nav2_params.yaml use_sim_time:=True

### nav2 with nav2_bringup (usually dont use this)

ros2 launch nav2_bringup navigation_launch.py use_sim_time:=True

when using nav2 you still need to create a map by moving around and having lidar generate a map. In the future we may have this update in real time with localization maybe

ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/diff_cont/cmd_vel_unstamped

rviz2 src/swarm_bot/config/view_bot.rviz    

## AMCL Adaptive Monte-Carlo Localization (Don't need)

YOU DO NOT NEED TO RUN THIS AS WE ARE NOT DOING LOCALIZATION

ros2 run nav2_amcl amcl --ros-args -p use_sim_time:=True

ros2 run nav2_util lifecycle_bringup amcl

This localizes the robot in the dyamic map we are creating, in the video by articul bot a map server is used, however that really just prints the topic of /map, slam tool box should be doing that too. 


### rviz with the cost map (run this last)

rviz2 src/swarm_bot/config/view_bot.rviz    

## Running ASLAM

The package will be ran from the package aslam. Launch scripts can be found in setup.py

### test setting goal

ros2 run aslam nav_test

## running aslam

ros2 run aslam aslam
