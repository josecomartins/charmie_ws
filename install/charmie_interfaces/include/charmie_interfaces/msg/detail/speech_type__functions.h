// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from charmie_interfaces:msg/SpeechType.idl
// generated code does not contain a copyright notice

#ifndef CHARMIE_INTERFACES__MSG__DETAIL__SPEECH_TYPE__FUNCTIONS_H_
#define CHARMIE_INTERFACES__MSG__DETAIL__SPEECH_TYPE__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "charmie_interfaces/msg/rosidl_generator_c__visibility_control.h"

#include "charmie_interfaces/msg/detail/speech_type__struct.h"

/// Initialize msg/SpeechType message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * charmie_interfaces__msg__SpeechType
 * )) before or use
 * charmie_interfaces__msg__SpeechType__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_charmie_interfaces
bool
charmie_interfaces__msg__SpeechType__init(charmie_interfaces__msg__SpeechType * msg);

/// Finalize msg/SpeechType message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_charmie_interfaces
void
charmie_interfaces__msg__SpeechType__fini(charmie_interfaces__msg__SpeechType * msg);

/// Create msg/SpeechType message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * charmie_interfaces__msg__SpeechType__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_charmie_interfaces
charmie_interfaces__msg__SpeechType *
charmie_interfaces__msg__SpeechType__create();

/// Destroy msg/SpeechType message.
/**
 * It calls
 * charmie_interfaces__msg__SpeechType__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_charmie_interfaces
void
charmie_interfaces__msg__SpeechType__destroy(charmie_interfaces__msg__SpeechType * msg);

/// Check for msg/SpeechType message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_charmie_interfaces
bool
charmie_interfaces__msg__SpeechType__are_equal(const charmie_interfaces__msg__SpeechType * lhs, const charmie_interfaces__msg__SpeechType * rhs);

/// Copy a msg/SpeechType message.
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
charmie_interfaces__msg__SpeechType__copy(
  const charmie_interfaces__msg__SpeechType * input,
  charmie_interfaces__msg__SpeechType * output);

/// Initialize array of msg/SpeechType messages.
/**
 * It allocates the memory for the number of elements and calls
 * charmie_interfaces__msg__SpeechType__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_charmie_interfaces
bool
charmie_interfaces__msg__SpeechType__Sequence__init(charmie_interfaces__msg__SpeechType__Sequence * array, size_t size);

/// Finalize array of msg/SpeechType messages.
/**
 * It calls
 * charmie_interfaces__msg__SpeechType__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_charmie_interfaces
void
charmie_interfaces__msg__SpeechType__Sequence__fini(charmie_interfaces__msg__SpeechType__Sequence * array);

/// Create array of msg/SpeechType messages.
/**
 * It allocates the memory for the array and calls
 * charmie_interfaces__msg__SpeechType__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_charmie_interfaces
charmie_interfaces__msg__SpeechType__Sequence *
charmie_interfaces__msg__SpeechType__Sequence__create(size_t size);

/// Destroy array of msg/SpeechType messages.
/**
 * It calls
 * charmie_interfaces__msg__SpeechType__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_charmie_interfaces
void
charmie_interfaces__msg__SpeechType__Sequence__destroy(charmie_interfaces__msg__SpeechType__Sequence * array);

/// Check for msg/SpeechType message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_charmie_interfaces
bool
charmie_interfaces__msg__SpeechType__Sequence__are_equal(const charmie_interfaces__msg__SpeechType__Sequence * lhs, const charmie_interfaces__msg__SpeechType__Sequence * rhs);

/// Copy an array of msg/SpeechType messages.
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
charmie_interfaces__msg__SpeechType__Sequence__copy(
  const charmie_interfaces__msg__SpeechType__Sequence * input,
  charmie_interfaces__msg__SpeechType__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // CHARMIE_INTERFACES__MSG__DETAIL__SPEECH_TYPE__FUNCTIONS_H_
