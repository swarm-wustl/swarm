// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from vslam:msg/PointCloudAndPose.idl
// generated code does not contain a copyright notice

#ifndef VSLAM__MSG__DETAIL__POINT_CLOUD_AND_POSE__TRAITS_HPP_
#define VSLAM__MSG__DETAIL__POINT_CLOUD_AND_POSE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "vslam/msg/detail/point_cloud_and_pose__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"
// Member 'pointcloud'
#include "sensor_msgs/msg/detail/point_cloud2__traits.hpp"
// Member 'pose'
#include "geometry_msgs/msg/detail/pose__traits.hpp"

namespace vslam
{

namespace msg
{

inline void to_flow_style_yaml(
  const PointCloudAndPose & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: pointcloud
  {
    out << "pointcloud: ";
    to_flow_style_yaml(msg.pointcloud, out);
    out << ", ";
  }

  // member: pose
  {
    out << "pose: ";
    to_flow_style_yaml(msg.pose, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const PointCloudAndPose & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }

  // member: pointcloud
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pointcloud:\n";
    to_block_style_yaml(msg.pointcloud, out, indentation + 2);
  }

  // member: pose
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pose:\n";
    to_block_style_yaml(msg.pose, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const PointCloudAndPose & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace vslam

namespace rosidl_generator_traits
{

[[deprecated("use vslam::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const vslam::msg::PointCloudAndPose & msg,
  std::ostream & out, size_t indentation = 0)
{
  vslam::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use vslam::msg::to_yaml() instead")]]
inline std::string to_yaml(const vslam::msg::PointCloudAndPose & msg)
{
  return vslam::msg::to_yaml(msg);
}

template<>
inline const char * data_type<vslam::msg::PointCloudAndPose>()
{
  return "vslam::msg::PointCloudAndPose";
}

template<>
inline const char * name<vslam::msg::PointCloudAndPose>()
{
  return "vslam/msg/PointCloudAndPose";
}

template<>
struct has_fixed_size<vslam::msg::PointCloudAndPose>
  : std::integral_constant<bool, has_fixed_size<geometry_msgs::msg::Pose>::value && has_fixed_size<sensor_msgs::msg::PointCloud2>::value && has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<vslam::msg::PointCloudAndPose>
  : std::integral_constant<bool, has_bounded_size<geometry_msgs::msg::Pose>::value && has_bounded_size<sensor_msgs::msg::PointCloud2>::value && has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<vslam::msg::PointCloudAndPose>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // VSLAM__MSG__DETAIL__POINT_CLOUD_AND_POSE__TRAITS_HPP_
