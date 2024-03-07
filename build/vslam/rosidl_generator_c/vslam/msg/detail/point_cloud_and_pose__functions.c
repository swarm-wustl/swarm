// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from vslam:msg/PointCloudAndPose.idl
// generated code does not contain a copyright notice
#include "vslam/msg/detail/point_cloud_and_pose__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `pointcloud`
#include "sensor_msgs/msg/detail/point_cloud2__functions.h"
// Member `pose`
#include "geometry_msgs/msg/detail/pose__functions.h"

bool
vslam__msg__PointCloudAndPose__init(vslam__msg__PointCloudAndPose * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    vslam__msg__PointCloudAndPose__fini(msg);
    return false;
  }
  // pointcloud
  if (!sensor_msgs__msg__PointCloud2__init(&msg->pointcloud)) {
    vslam__msg__PointCloudAndPose__fini(msg);
    return false;
  }
  // pose
  if (!geometry_msgs__msg__Pose__init(&msg->pose)) {
    vslam__msg__PointCloudAndPose__fini(msg);
    return false;
  }
  return true;
}

void
vslam__msg__PointCloudAndPose__fini(vslam__msg__PointCloudAndPose * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // pointcloud
  sensor_msgs__msg__PointCloud2__fini(&msg->pointcloud);
  // pose
  geometry_msgs__msg__Pose__fini(&msg->pose);
}

bool
vslam__msg__PointCloudAndPose__are_equal(const vslam__msg__PointCloudAndPose * lhs, const vslam__msg__PointCloudAndPose * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->header), &(rhs->header)))
  {
    return false;
  }
  // pointcloud
  if (!sensor_msgs__msg__PointCloud2__are_equal(
      &(lhs->pointcloud), &(rhs->pointcloud)))
  {
    return false;
  }
  // pose
  if (!geometry_msgs__msg__Pose__are_equal(
      &(lhs->pose), &(rhs->pose)))
  {
    return false;
  }
  return true;
}

bool
vslam__msg__PointCloudAndPose__copy(
  const vslam__msg__PointCloudAndPose * input,
  vslam__msg__PointCloudAndPose * output)
{
  if (!input || !output) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__copy(
      &(input->header), &(output->header)))
  {
    return false;
  }
  // pointcloud
  if (!sensor_msgs__msg__PointCloud2__copy(
      &(input->pointcloud), &(output->pointcloud)))
  {
    return false;
  }
  // pose
  if (!geometry_msgs__msg__Pose__copy(
      &(input->pose), &(output->pose)))
  {
    return false;
  }
  return true;
}

vslam__msg__PointCloudAndPose *
vslam__msg__PointCloudAndPose__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  vslam__msg__PointCloudAndPose * msg = (vslam__msg__PointCloudAndPose *)allocator.allocate(sizeof(vslam__msg__PointCloudAndPose), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(vslam__msg__PointCloudAndPose));
  bool success = vslam__msg__PointCloudAndPose__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
vslam__msg__PointCloudAndPose__destroy(vslam__msg__PointCloudAndPose * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    vslam__msg__PointCloudAndPose__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
vslam__msg__PointCloudAndPose__Sequence__init(vslam__msg__PointCloudAndPose__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  vslam__msg__PointCloudAndPose * data = NULL;

  if (size) {
    data = (vslam__msg__PointCloudAndPose *)allocator.zero_allocate(size, sizeof(vslam__msg__PointCloudAndPose), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = vslam__msg__PointCloudAndPose__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        vslam__msg__PointCloudAndPose__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
vslam__msg__PointCloudAndPose__Sequence__fini(vslam__msg__PointCloudAndPose__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      vslam__msg__PointCloudAndPose__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

vslam__msg__PointCloudAndPose__Sequence *
vslam__msg__PointCloudAndPose__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  vslam__msg__PointCloudAndPose__Sequence * array = (vslam__msg__PointCloudAndPose__Sequence *)allocator.allocate(sizeof(vslam__msg__PointCloudAndPose__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = vslam__msg__PointCloudAndPose__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
vslam__msg__PointCloudAndPose__Sequence__destroy(vslam__msg__PointCloudAndPose__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    vslam__msg__PointCloudAndPose__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
vslam__msg__PointCloudAndPose__Sequence__are_equal(const vslam__msg__PointCloudAndPose__Sequence * lhs, const vslam__msg__PointCloudAndPose__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!vslam__msg__PointCloudAndPose__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
vslam__msg__PointCloudAndPose__Sequence__copy(
  const vslam__msg__PointCloudAndPose__Sequence * input,
  vslam__msg__PointCloudAndPose__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(vslam__msg__PointCloudAndPose);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    vslam__msg__PointCloudAndPose * data =
      (vslam__msg__PointCloudAndPose *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!vslam__msg__PointCloudAndPose__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          vslam__msg__PointCloudAndPose__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!vslam__msg__PointCloudAndPose__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
