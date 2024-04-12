# ASLAM

Aslam stands for active-slam, in which uses slam to actively make decisions

AT CURRENT ITERATION this version uses LIDAR slam and is still WIP 

## setup

install these packages

- sudo apt install ros-humble-navigation2
- sudo apt install ros-humble-nav2-bringup
- sudo apt install ros-humble-twist-mux
- sudo apt install ros-humble-slam-toolbox

## running

run these commands in /ros directory

### apartment map and running gazebo

ros2 launch swarm_bot launch_sim.launch.py world:=./src/swarm_bot/worlds/apartmentswag.world

### maze map and running gazebo

ros2 launch swarm_bot launch_sim.launch.py world:=./src/swarm_bot/worlds/maze_swarm_map.world

### Async SLam

ros2 launch slam_toolbox online_async_launch.py params_file:=./src/swarm_bot/config/mapper_params_online_async.yaml use_sim_time:=true

### nav2 

ros2 launch swarm_bot navigation.launch.py use_sim_time:=true

### nav2 with nav2_bringup (usually dont use this)

ros2 launch nav2_bringup navigation.launch.py use_sim_time:=true

### twist mux 

only run if the launch twist mux not working and the robot doesnt move when given a goal

ros2 run twist_mux twist_mux --ros-args --params-file ./src/swarm_bot/config/twist_mux.yaml -r cmd_vel_out:=diff_cont/cmd_vel_unstamped

### teleop manual controlling

when using nav2 you still need to create a map by moving around and having lidar generate a map. In the future we may have this update in real time with localization maybe

ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/diff_cont/cmd_vel_unstamped

rviz2 src/swarm_bot/config/view_bot.rviz    

### rviz with the cost map (run this last)

rviz2 src/swarm_bot/config/view_bot.rviz    
