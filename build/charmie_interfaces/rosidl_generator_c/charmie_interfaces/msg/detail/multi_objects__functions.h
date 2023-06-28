// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from charmie_interfaces:msg/MultiObjects.idl
// generated code does not contain a copyright notice

#ifndef CHARMIE_INTERFACES__MSG__DETAIL__MULTI_OBJECTS__FUNCTIONS_H_
#define CHARMIE_INTERFACES__MSG__DETAIL__MULTI_OBJECTS__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "charmie_interfaces/msg/rosidl_generator_c__visibility_control.h"

#include "charmie_interfaces/msg/detail/multi_objects__struct.h"

/// Initialize msg/MultiObjects message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * charmie_interfaces__msg__MultiObjects
 * )) before or use
 * charmie_interfaces__msg__MultiObjects__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_charmie_interfaces
bool
charmie_interfaces__msg__MultiObjects__init(charmie_interfaces__msg__MultiObjects * msg);

/// Finalize msg/MultiObjects message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_charmie_interfaces
void
charmie_interfaces__msg__MultiObjects__fini(charmie_interfaces__msg__MultiObjects * msg);

/// Create msg/MultiObjects message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * charmie_interfaces__msg__MultiObjects__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_charmie_interfaces
charmie_interfaces__msg__MultiObjects *
charmie_interfaces__msg__MultiObjects__create();

/// Destroy msg/MultiObjects message.
/**
 * It calls
 * charmie_interfaces__msg__MultiObjects__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_charmie_interfaces
void
charmie_interfaces__msg__MultiObjects__destroy(charmie_interfaces__msg__MultiObjects * msg);

/// Check for msg/MultiObjects message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_charmie_interfaces
bool
charmie_interfaces__msg__MultiObjects__are_equal(const charmie_interfaces__msg__MultiObjects * lhs, const charmie_interfaces__msg__MultiObjects * rhs);

/// Copy a msg/MultiObjects message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_charmie_interfaces
bool
charmie_interfaces__msg__MultiObjects__copy(
  const charmie_interfaces__msg__MultiObjects * input,
  charmie_interfaces__msg__MultiObjects * output);

/// Initialize array of msg/MultiObjects messages.
/**
 * It allocates the memory for the number of elements and calls
 * charmie_interfaces__msg__MultiObjects__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_charmie_interfaces
bool
charmie_interfaces__msg__MultiObjects__Sequence__init(charmie_interfaces__msg__MultiObjects__Sequence * array, size_t size);

/// Finalize array of msg/MultiObjects messages.
/**
 * It calls
 * charmie_interfaces__msg__MultiObjects__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_charmie_interfaces
void
charmie_interfaces__msg__MultiObjects__Sequence__fini(charmie_interfaces__msg__MultiObjects__Sequence * array);

/// Create array of msg/MultiObjects messages.
/**
 * It allocates the memory for the array and calls
 * charmie_interfaces__msg__MultiObjects__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_charmie_interfaces
charmie_interfaces__msg__MultiObjects__Sequence *
charmie_interfaces__msg__MultiObjects__Sequence__create(size_t size);

/// Destroy array of msg/MultiObjects messages.
/**
 * It calls
 * charmie_interfaces__msg__MultiObjects__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_charmie_interfaces
void
charmie_interfaces__msg__MultiObjects__Sequence__destroy(charmie_interfaces__msg__MultiObjects__Sequence * array);

/// Check for msg/MultiObjects message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_charmie_interfaces
bool
charmie_interfaces__msg__MultiObjects__Sequence__are_equal(const charmie_interfaces__msg__MultiObjects__Sequence * lhs, const charmie_interfaces__msg__MultiObjects__Sequence * rhs);

/// Copy an array of msg/MultiObjects messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_charmie_interfaces
bool
charmie_interfaces__msg__MultiObjects__Sequence__copy(
  const charmie_interfaces__msg__MultiObjects__Sequence * input,
  charmie_interfaces__msg__MultiObjects__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // CHARMIE_INTERFACES__MSG__DETAIL__MULTI_OBJECTS__FUNCTIONS_H_
