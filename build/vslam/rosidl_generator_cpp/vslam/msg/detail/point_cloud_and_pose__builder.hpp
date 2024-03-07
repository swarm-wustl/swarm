// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from vslam:msg/PointCloudAndPose.idl
// generated code does not contain a copyright notice

#ifndef VSLAM__MSG__DETAIL__POINT_CLOUD_AND_POSE__BUILDER_HPP_
#define VSLAM__MSG__DETAIL__POINT_CLOUD_AND_POSE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "vslam/msg/detail/point_cloud_and_pose__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace vslam
{

namespace msg
{

namespace builder
{

class Init_PointCloudAndPose_pose
{
public:
  explicit Init_PointCloudAndPose_pose(::vslam::msg::PointCloudAndPose & msg)
  : msg_(msg)
  {}
  ::vslam::msg::PointCloudAndPose pose(::vslam::msg::PointCloudAndPose::_pose_type arg)
  {
    msg_.pose = std::move(arg);
    return std::move(msg_);
  }

private:
  ::vslam::msg::PointCloudAndPose msg_;
};

class Init_PointCloudAndPose_pointcloud
{
public:
  explicit Init_PointCloudAndPose_pointcloud(::vslam::msg::PointCloudAndPose & msg)
  : msg_(msg)
  {}
  Init_PointCloudAndPose_pose pointcloud(::vslam::msg::PointCloudAndPose::_pointcloud_type arg)
  {
    msg_.pointcloud = std::move(arg);
    return Init_PointCloudAndPose_pose(msg_);
  }

private:
  ::vslam::msg::PointCloudAndPose msg_;
};

class Init_PointCloudAndPose_header
{
public:
  Init_PointCloudAndPose_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_PointCloudAndPose_pointcloud header(::vslam::msg::PointCloudAndPose::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_PointCloudAndPose_pointcloud(msg_);
  }

private:
  ::vslam::msg::PointCloudAndPose msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::vslam::msg::PointCloudAndPose>()
{
  return vslam::msg::builder::Init_PointCloudAndPose_header();
}

}  // namespace vslam

#endif  // VSLAM__MSG__DETAIL__POINT_CLOUD_AND_POSE__BUILDER_HPP_
