# URDF Description of Model Robot for Simulation

Contains files to describe and simulate the robot

- `description/` has URDF files containing the design of the robot
- `worlds/` has Gazebo environments the robot can exist in (eventually a replica of the maze can be built here)
- `launch/` has files for launching the simulations (see below)
- `config/` has files for viewing the robot in RViz

## Install

Install additional dependencies for ROS

```
sudo apt install ros-humble-ros-gz ros-humble-gazebo-ros-pkgs ros-humble-xacro ros-humble-joint-state-publisher-gui ros-humble-ros2-control ros-humble-ros2-controllers ros-humble-ros2-control ros-humble-twist-stamper ros-humble-vision-opencv ros-humble-message-filters
```

## To Run

Remember to always run `source install/setup.bash` in a terminal before using ROS2 commands. If the `install` directory does not yet exist, first build the workspace (see below).

### Build
Run after making file changes

```
colcon build --symlink-install --packages-select swarm_bot
```

### Launch Gazebo
Gazebo is the physics/environment simulator for the robot

```
ros2 launch swarm_bot launch_sim.launch.py world:=./src/swarm_bot/worlds/random_env.world
```

#### Control With Keyboard
Open this in a terminal and input keys into it to control the robot in Gazebo

```
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/diff_cont/cmd_vel_unstamped
```

### World with maze (Jaxon)

```
ros2 launch swarm_bot launch_sim.launch.py world:=./src/swarm_bot/worlds/maze_swarm_map.world
```

maze model should be located in the models folder in the base root of the repo

#### Control With Xbox Joystick

First, verify that the controller is properly connected to the computer using the [`jstest-gtk` utility](https://github.com/Grumbel/jstest-gtk).

Then, run the following command:

```
ros2 launch swarm_bot joystick.launch.py
```

#### Ball Tracking Example

Ball tracking would work. If you want to set it up, follow this [tutorial](https://www.youtube.com/watch?v=gISSSbYUZag)

### Launch RViz
RViz visualizes the robot. In contrast to Gazebo, it doesn't run physics simulations but is better for prototyping and debugging

```
rviz2 src/swarm_bot/config/view_bot.rviz                    
```

# VSLAM

See the [VSLAM README](/ros/src/swarm_bot/vslam/README.md) for more information on how to run the VSLAM system.

