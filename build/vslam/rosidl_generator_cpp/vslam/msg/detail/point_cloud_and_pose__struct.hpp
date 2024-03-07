// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from vslam:msg/PointCloudAndPose.idl
// generated code does not contain a copyright notice

#ifndef VSLAM__MSG__DETAIL__POINT_CLOUD_AND_POSE__STRUCT_HPP_
#define VSLAM__MSG__DETAIL__POINT_CLOUD_AND_POSE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.hpp"
// Member 'pointcloud'
#include "sensor_msgs/msg/detail/point_cloud2__struct.hpp"
// Member 'pose'
#include "geometry_msgs/msg/detail/pose__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__vslam__msg__PointCloudAndPose __attribute__((deprecated))
#else
# define DEPRECATED__vslam__msg__PointCloudAndPose __declspec(deprecated)
#endif

namespace vslam
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct PointCloudAndPose_
{
  using Type = PointCloudAndPose_<ContainerAllocator>;

  explicit PointCloudAndPose_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init),
    pointcloud(_init),
    pose(_init)
  {
    (void)_init;
  }

  explicit PointCloudAndPose_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    pointcloud(_alloc, _init),
    pose(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _pointcloud_type =
    sensor_msgs::msg::PointCloud2_<ContainerAllocator>;
  _pointcloud_type pointcloud;
  using _pose_type =
    geometry_msgs::msg::Pose_<ContainerAllocator>;
  _pose_type pose;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__pointcloud(
    const sensor_msgs::msg::PointCloud2_<ContainerAllocator> & _arg)
  {
    this->pointcloud = _arg;
    return *this;
  }
  Type & set__pose(
    const geometry_msgs::msg::Pose_<ContainerAllocator> & _arg)
  {
    this->pose = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    vslam::msg::PointCloudAndPose_<ContainerAllocator> *;
  using ConstRawPtr =
    const vslam::msg::PointCloudAndPose_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<vslam::msg::PointCloudAndPose_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<vslam::msg::PointCloudAndPose_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      vslam::msg::PointCloudAndPose_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<vslam::msg::PointCloudAndPose_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      vslam::msg::PointCloudAndPose_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<vslam::msg::PointCloudAndPose_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<vslam::msg::PointCloudAndPose_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<vslam::msg::PointCloudAndPose_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__vslam__msg__PointCloudAndPose
    std::shared_ptr<vslam::msg::PointCloudAndPose_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__vslam__msg__PointCloudAndPose
    std::shared_ptr<vslam::msg::PointCloudAndPose_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const PointCloudAndPose_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->pointcloud != other.pointcloud) {
      return false;
    }
    if (this->pose != other.pose) {
      return false;
    }
    return true;
  }
  bool operator!=(const PointCloudAndPose_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct PointCloudAndPose_

// alias to use template instance with default allocator
using PointCloudAndPose =
  vslam::msg::PointCloudAndPose_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace vslam

#endif  // VSLAM__MSG__DETAIL__POINT_CLOUD_AND_POSE__STRUCT_HPP_
