// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from vslam:msg/PointCloudAndPose.idl
// generated code does not contain a copyright notice

#ifndef VSLAM__MSG__DETAIL__POINT_CLOUD_AND_POSE__STRUCT_H_
#define VSLAM__MSG__DETAIL__POINT_CLOUD_AND_POSE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'pointcloud'
#include "sensor_msgs/msg/detail/point_cloud2__struct.h"
// Member 'pose'
#include "geometry_msgs/msg/detail/pose__struct.h"

/// Struct defined in msg/PointCloudAndPose in the package vslam.
typedef struct vslam__msg__PointCloudAndPose
{
  std_msgs__msg__Header header;
  sensor_msgs__msg__PointCloud2 pointcloud;
  geometry_msgs__msg__Pose pose;
} vslam__msg__PointCloudAndPose;

// Struct for a sequence of vslam__msg__PointCloudAndPose.
typedef struct vslam__msg__PointCloudAndPose__Sequence
{
  vslam__msg__PointCloudAndPose * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} vslam__msg__PointCloudAndPose__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // VSLAM__MSG__DETAIL__POINT_CLOUD_AND_POSE__STRUCT_H_
