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

## Install ORB_SLAM3
First, you will need to build ORB_SLAM3 and its dependencies. Follow the instructions [here](https://github.com/bharath5673/ORB-SLAM3) to do so. After completing these instructions, you should have a folder `~/Dev` that contains `ORB_SLAM3`. Ensure that it functions by running an example.

```
cd ~/Dev/ORB_SLAM3
./Examples/Monocular/mono_euroc ./Vocabulary/ORBvoc.txt ./Examples/Monocular/EuRoC.yaml ~/Datasets/EuRoC/MH01 ./Examples/Monocular/EuRoC_TimeStamps/MH01.txt
```

If the video feed does not appear, edit the source file `Examples/Monocular/mono_euroc.cc` and change line 83 to `ORB_SLAM3::System SLAM(argv[1],argv[2],ORB_SLAM3::System::MONOCULAR, true);` (false has been swapped to true).

## Build ROS2 Wrapper
Build the ROS2 wrapper for ORB_SLAM3. This will allow us to use ORB_SLAM3 as a ROS2 node. From the `swarm/ros` directory, run the following command:

```
colcon build --packages-select ros2orbslam3
```

### Potential Errors
These errors likely indicate an issue with the installation of ORB_SLAM3 or its dependencies.

- `fatal error: Eigen/Dense: No such file or directory`. If Eigen is installed, you may need to create a symlink as follows: `sudo ln -sf /usr/local/include/eigen3/Eigen /usr/local/include/Eigen`
- `/usr/local/include/pangolin/gl/gl.hpp:335:5: error: ‘glCopyImageSubDataNV’ was not declared in this scope` (and similar Pangolin errors): First, ensure that you are building version 0.6 of Pangolin with `git checkout v0.6`. Then add the line `#include <limits>` to the top of `colour.h`. Remember that the Pangolin repo should be installed to `~/Dev/Pangolin`.
- `libpango_windowing.so: cannot open shared object file: No such file or directory`. Run `sudo ldconfig` to configure dynamic linker runtime bindings.

## Run
To run ORB_SLAM3, first launch the simulation as described above (use the `vslam_env.world` environment, as it contains more detailed graphics for ORB SLAM3 to recognize). Then, run the following command:

```
ros2 run ros2orbslam3 mono
```

If the annotated video feed does not appear, try moving the robot around to a place with more detail (e.g. near a wall).

Support for stereo, RGB-D, and IMU variants is not yet implemented.

