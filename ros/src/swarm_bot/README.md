# URDF Description of Model Robot for Simulation

Contains files to describe and simulate the robot

- `description/` has URDF files containing the design of the robot
- `worlds/` has Gazebo environments the robot can exist in (eventually a replica of the maze can be built here)
- `launch/` has files for launching the simulations (see below)
- `config/` has files for viewing the robot in RViz

## Install

After installing ROS 2, also install xacro ans the joint state publisher GUI.

```
sudo apt install ros-humble-xacro ros-humble-joint-state-publisher-gui ros-humble-ros2-control ros-humble-ros2-controllers ros-humble-gazebo-ros2-control
```

## To Run

Remember to always run `source install/setup.bash` in a terminal before using ROS2 commands

### Build
Run after making file changes

```
$/ros
colcon build --symlink-install
```

### Launch Gazebo
Gazebo is the physics/environment simulator for the robot

```
$/ros
ros2 launch swarm_bot launch_sim.launch.py world:=./src/swarm_bot/worlds/random_env.world
```

#### Control With Teleop
Open this in a terminal and input keys into it to control the robot in Gazebo

```
$/ros
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Can also use `teleop_twist_joystick` if one is available

### Launch RViz
RViz visualizes the robot. In contrast to Gazebo, it doesn't run physics simulations but is better for prototyping and debugging

```
$/ros
rviz2 src/swarm_bot/config/view_bot.rviz                    
```

