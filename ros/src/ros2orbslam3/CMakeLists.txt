cmake_minimum_required(VERSION 3.8)
project(ros2orbslam3)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)

find_package(image_transport REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(OpenCV REQUIRED)

find_package(Eigen3 REQUIRED)
find_package(Pangolin REQUIRED)

include_directories(
  ~/Dev/ORB_SLAM3/include
  ~/Dev/ORB_SLAM3/include/CameraModels
  ~/Dev/ORB_SLAM3/include/ThirdParty/Sophus
  ~/Dev/ORB_SLAM3/ThirdParty/Sophus
  ~/Dev/ORB_SLAM3/ThirdParty/DBoW2/DBoW2
  ~/Dev/ORB_SLAM3/ThirdParty/DBoW2
  ~/Dev/ORB_SLAM3/ThirdParty
  ~/Dev/ORB_SLAM3/
  ${EIGEN3_INCLUDE_DIR}
  ${Pangolin_INCLUDE_DIRS}
)

add_executable(mono src/mono_orb_slam3_node.cpp)
ament_target_dependencies(mono rclcpp std_msgs nav_msgs sensor_msgs image_transport cv_bridge OpenCV)

add_executable(grid_mapper src/grid_mapper.cpp)
ament_target_dependencies(grid_mapper rclcpp std_msgs sensor_msgs geometry_msgs OpenCV)

add_executable(video_reader src/video_reader.cpp)
ament_target_dependencies(video_reader rclcpp std_msgs sensor_msgs cv_bridge OpenCV)


link_directories(
  ~/Dev/ORB_SLAM3/Thirdparty/Pangolin/build
)

target_link_libraries(mono
  ${OpenCV_LIBS}
  ${EIGEN3_LIBS}
  ${Pangolin_LIBRARIES}
  ~/Dev/ORB_SLAM3/Thirdparty/DBoW2/lib/libDBoW2.so
  ~/Dev/ORB_SLAM3/Thirdparty/g2o/lib/libg2o.so
  ~/Dev/ORB_SLAM3/lib/libORB_SLAM3.so
  -lboost_system
  -lboost_serialization
  -lcrypto
  -lGL  # Link against OpenGL
  -lGLU  # Link against GLU
)

target_link_libraries(grid_mapper)
target_link_libraries(video_reader)

set(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_RPATH}:~/ORB_SLAM3/Thirdparty/Pangolin/build")

install(TARGETS
  mono
  DESTINATION lib/${PROJECT_NAME})

install(TARGETS
  grid_mapper
  DESTINATION lib/${PROJECT_NAME})

install(TARGETS
  video_reader
  DESTINATION lib/${PROJECT_NAME})

ament_package()
