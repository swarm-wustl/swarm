// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__rosidl_typesupport_fastrtps_cpp.hpp.em
// with input from vslam:msg/PointCloudAndPose.idl
// generated code does not contain a copyright notice

#ifndef VSLAM__MSG__DETAIL__POINT_CLOUD_AND_POSE__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
#define VSLAM__MSG__DETAIL__POINT_CLOUD_AND_POSE__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_

#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "vslam/msg/rosidl_typesupport_fastrtps_cpp__visibility_control.h"
#include "vslam/msg/detail/point_cloud_and_pose__struct.hpp"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

#include "fastcdr/Cdr.h"

namespace vslam
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_vslam
cdr_serialize(
  const vslam::msg::PointCloudAndPose & ros_message,
  eprosima::fastcdr::Cdr & cdr);

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_vslam
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  vslam::msg::PointCloudAndPose & ros_message);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_vslam
get_serialized_size(
  const vslam::msg::PointCloudAndPose & ros_message,
  size_t current_alignment);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_vslam
max_serialized_size_PointCloudAndPose(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace vslam

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_vslam
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, vslam, msg, PointCloudAndPose)();

#ifdef __cplusplus
}
#endif

#endif  // VSLAM__MSG__DETAIL__POINT_CLOUD_AND_POSE__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
