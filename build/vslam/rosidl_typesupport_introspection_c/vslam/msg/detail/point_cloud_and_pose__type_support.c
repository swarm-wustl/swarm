// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from vslam:msg/PointCloudAndPose.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "vslam/msg/detail/point_cloud_and_pose__rosidl_typesupport_introspection_c.h"
#include "vslam/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "vslam/msg/detail/point_cloud_and_pose__functions.h"
#include "vslam/msg/detail/point_cloud_and_pose__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `pointcloud`
#include "sensor_msgs/msg/point_cloud2.h"
// Member `pointcloud`
#include "sensor_msgs/msg/detail/point_cloud2__rosidl_typesupport_introspection_c.h"
// Member `pose`
#include "geometry_msgs/msg/pose.h"
// Member `pose`
#include "geometry_msgs/msg/detail/pose__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void vslam__msg__PointCloudAndPose__rosidl_typesupport_introspection_c__PointCloudAndPose_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  vslam__msg__PointCloudAndPose__init(message_memory);
}

void vslam__msg__PointCloudAndPose__rosidl_typesupport_introspection_c__PointCloudAndPose_fini_function(void * message_memory)
{
  vslam__msg__PointCloudAndPose__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember vslam__msg__PointCloudAndPose__rosidl_typesupport_introspection_c__PointCloudAndPose_message_member_array[3] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(vslam__msg__PointCloudAndPose, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "pointcloud",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(vslam__msg__PointCloudAndPose, pointcloud),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "pose",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(vslam__msg__PointCloudAndPose, pose),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers vslam__msg__PointCloudAndPose__rosidl_typesupport_introspection_c__PointCloudAndPose_message_members = {
  "vslam__msg",  // message namespace
  "PointCloudAndPose",  // message name
  3,  // number of fields
  sizeof(vslam__msg__PointCloudAndPose),
  vslam__msg__PointCloudAndPose__rosidl_typesupport_introspection_c__PointCloudAndPose_message_member_array,  // message members
  vslam__msg__PointCloudAndPose__rosidl_typesupport_introspection_c__PointCloudAndPose_init_function,  // function to initialize message memory (memory has to be allocated)
  vslam__msg__PointCloudAndPose__rosidl_typesupport_introspection_c__PointCloudAndPose_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t vslam__msg__PointCloudAndPose__rosidl_typesupport_introspection_c__PointCloudAndPose_message_type_support_handle = {
  0,
  &vslam__msg__PointCloudAndPose__rosidl_typesupport_introspection_c__PointCloudAndPose_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_vslam
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, vslam, msg, PointCloudAndPose)() {
  vslam__msg__PointCloudAndPose__rosidl_typesupport_introspection_c__PointCloudAndPose_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  vslam__msg__PointCloudAndPose__rosidl_typesupport_introspection_c__PointCloudAndPose_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, sensor_msgs, msg, PointCloud2)();
  vslam__msg__PointCloudAndPose__rosidl_typesupport_introspection_c__PointCloudAndPose_message_member_array[2].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Pose)();
  if (!vslam__msg__PointCloudAndPose__rosidl_typesupport_introspection_c__PointCloudAndPose_message_type_support_handle.typesupport_identifier) {
    vslam__msg__PointCloudAndPose__rosidl_typesupport_introspection_c__PointCloudAndPose_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &vslam__msg__PointCloudAndPose__rosidl_typesupport_introspection_c__PointCloudAndPose_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
