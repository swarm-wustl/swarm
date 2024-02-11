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
colcon build --packages-select vslam
```

### Potential Errors
These errors likely indicate an issue with the installation of ORB_SLAM3 or its dependencies.

- `fatal error: Eigen/Dense: No such file or directory`. If Eigen is installed, you may need to create a symlink as follows: `sudo ln -sf /usr/local/include/eigen3/Eigen /usr/local/include/Eigen`
- `/usr/local/include/pangolin/gl/gl.hpp:335:5: error: ‘glCopyImageSubDataNV’ was not declared in this scope` (and similar Pangolin errors): First, ensure that you are building version 0.6 of Pangolin with `git checkout v0.6`. Then add the line `#include <limits>` to the top of `colour.h`. Remember that the Pangolin repo should be installed to `~/Dev/Pangolin`.
- `libpango_windowing.so: cannot open shared object file: No such file or directory`. Run `sudo ldconfig` to configure dynamic linker runtime bindings.
- `error while loading shared libraries: libORB_SLAM3.so: cannot open shared object file: No such file or directory`: Run the following command to update LD library: `export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/$(whoami)/Dev/ORB_SLAM3/lib`

- `fatal error: sophus/s3.hpp: No such file or directory.` Run the following commands:
```
cd ~/Dev/ORB_SLAM3/Thirdparty/Sophus
cmake .
make
sudo make install
```


## Run

### Getting a Camera Video Input
The `system` node subscribes to `camera/image_raw`. In order for this topic to be published, either launch the Gazebo simulation with the `vslam_env.world` environment or run the following to publish the frames from a video in the `samples/` directory:

```
ros2 run vslam video_reader --ros-args -p "video_file_name:=maze_traversal.mov"
```

### Running the Node
To run the `system` node, run:

```
ros2 run vslam system
```

If the annotated video feed does not appear, try moving the robot around to a place with more detail (e.g. near a wall).

Support for stereo, RGB-D, and IMU variants is not yet implemented.

