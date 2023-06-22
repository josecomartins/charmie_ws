// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from charmie_interfaces:msg/ObstacleInfo.idl
// generated code does not contain a copyright notice
#include "charmie_interfaces/msg/detail/obstacle_info__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


bool
charmie_interfaces__msg__ObstacleInfo__init(charmie_interfaces__msg__ObstacleInfo * msg)
{
  if (!msg) {
    return false;
  }
  // alfa
  // dist
  // length_cm
  // length_degrees
  return true;
}

void
charmie_interfaces__msg__ObstacleInfo__fini(charmie_interfaces__msg__ObstacleInfo * msg)
{
  if (!msg) {
    return;
  }
  // alfa
  // dist
  // length_cm
  // length_degrees
}

bool
charmie_interfaces__msg__ObstacleInfo__are_equal(const charmie_interfaces__msg__ObstacleInfo * lhs, const charmie_interfaces__msg__ObstacleInfo * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // alfa
  if (lhs->alfa != rhs->alfa) {
    return false;
  }
  // dist
  if (lhs->dist != rhs->dist) {
    return false;
  }
  // length_cm
  if (lhs->length_cm != rhs->length_cm) {
    return false;
  }
  // length_degrees
  if (lhs->length_degrees != rhs->length_degrees) {
    return false;
  }
  return true;
}

bool
charmie_interfaces__msg__ObstacleInfo__copy(
  const charmie_interfaces__msg__ObstacleInfo * input,
  charmie_interfaces__msg__ObstacleInfo * output)
{
  if (!input || !output) {
    return false;
  }
  // alfa
  output->alfa = input->alfa;
  // dist
  output->dist = input->dist;
  // length_cm
  output->length_cm = input->length_cm;
  // length_degrees
  output->length_degrees = input->length_degrees;
  return true;
}

charmie_interfaces__msg__ObstacleInfo *
charmie_interfaces__msg__ObstacleInfo__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  charmie_interfaces__msg__ObstacleInfo * msg = (charmie_interfaces__msg__ObstacleInfo *)allocator.allocate(sizeof(charmie_interfaces__msg__ObstacleInfo), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(charmie_interfaces__msg__ObstacleInfo));
  bool success = charmie_interfaces__msg__ObstacleInfo__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
charmie_interfaces__msg__ObstacleInfo__destroy(charmie_interfaces__msg__ObstacleInfo * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    charmie_interfaces__msg__ObstacleInfo__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
charmie_interfaces__msg__ObstacleInfo__Sequence__init(charmie_interfaces__msg__ObstacleInfo__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  charmie_interfaces__msg__ObstacleInfo * data = NULL;

  if (size) {
    data = (charmie_interfaces__msg__ObstacleInfo *)allocator.zero_allocate(size, sizeof(charmie_interfaces__msg__ObstacleInfo), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = charmie_interfaces__msg__ObstacleInfo__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        charmie_interfaces__msg__ObstacleInfo__fini(&data[i - 1]);
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
charmie_interfaces__msg__ObstacleInfo__Sequence__fini(charmie_interfaces__msg__ObstacleInfo__Sequence * array)
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
      charmie_interfaces__msg__ObstacleInfo__fini(&array->data[i]);
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

charmie_interfaces__msg__ObstacleInfo__Sequence *
charmie_interfaces__msg__ObstacleInfo__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  charmie_interfaces__msg__ObstacleInfo__Sequence * array = (charmie_interfaces__msg__ObstacleInfo__Sequence *)allocator.allocate(sizeof(charmie_interfaces__msg__ObstacleInfo__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = charmie_interfaces__msg__ObstacleInfo__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
charmie_interfaces__msg__ObstacleInfo__Sequence__destroy(charmie_interfaces__msg__ObstacleInfo__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    charmie_interfaces__msg__ObstacleInfo__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
charmie_interfaces__msg__ObstacleInfo__Sequence__are_equal(const charmie_interfaces__msg__ObstacleInfo__Sequence * lhs, const charmie_interfaces__msg__ObstacleInfo__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!charmie_interfaces__msg__ObstacleInfo__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
charmie_interfaces__msg__ObstacleInfo__Sequence__copy(
  const charmie_interfaces__msg__ObstacleInfo__Sequence * input,
  charmie_interfaces__msg__ObstacleInfo__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(charmie_interfaces__msg__ObstacleInfo);
    charmie_interfaces__msg__ObstacleInfo * data =
      (charmie_interfaces__msg__ObstacleInfo *)realloc(output->data, allocation_size);
    if (!data) {
      return false;
    }
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!charmie_interfaces__msg__ObstacleInfo__init(&data[i])) {
        /* free currently allocated and return false */
        for (; i-- > output->capacity; ) {
          charmie_interfaces__msg__ObstacleInfo__fini(&data[i]);
        }
        free(data);
        return false;
      }
    }
    output->data = data;
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!charmie_interfaces__msg__ObstacleInfo__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
