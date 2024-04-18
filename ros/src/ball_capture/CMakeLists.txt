cmake_minimum_required(VERSION 3.8)
project(ball_capture)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(image_transport REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(OpenCV REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(std_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(common REQUIRED)

# add executables
add_executable(detect_ball src/detect_ball.cpp)
ament_target_dependencies(detect_ball rclcpp sensor_msgs image_transport cv_bridge OpenCV common)

add_executable(capture_ball src/capture_ball.cpp)
ament_target_dependencies(capture_ball rclcpp sensor_msgs geometry_msgs)

# Custom messages, services, and actions
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/DetectedBall.msg"
  DEPENDENCIES
  builtin_interfaces
  std_msgs
  rosidl_default_generators
)
rosidl_get_typesupport_target(cpp_typesupport_target ${PROJECT_NAME} "rosidl_typesupport_cpp")
target_link_libraries(detect_ball ${cpp_typesupport_target})
target_link_libraries(capture_ball ${cpp_typesupport_target})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

install(TARGETS
  detect_ball
  DESTINATION lib/${PROJECT_NAME}
)

install(TARGETS
  capture_ball
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
