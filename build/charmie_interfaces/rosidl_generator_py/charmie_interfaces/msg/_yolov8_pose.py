# generated from rosidl_generator_py/resource/_idl.py.em
# with input from charmie_interfaces:msg/Yolov8Pose.idl
# generated code does not contain a copyright notice


# Import statements for member types

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_Yolov8Pose(type):
    """Metaclass of message 'Yolov8Pose'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('charmie_interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'charmie_interfaces.msg.Yolov8Pose')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__yolov8_pose
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__yolov8_pose
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__yolov8_pose
            cls._TYPE_SUPPORT = module.type_support_msg__msg__yolov8_pose
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__yolov8_pose

            from charmie_interfaces.msg import DetectedPerson
            if DetectedPerson.__class__._TYPE_SUPPORT is None:
                DetectedPerson.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class Yolov8Pose(metaclass=Metaclass_Yolov8Pose):
    """Message class 'Yolov8Pose'."""

    __slots__ = [
        '_num_person',
        '_persons',
    ]

    _fields_and_field_types = {
        'num_person': 'int32',
        'persons': 'sequence<charmie_interfaces/DetectedPerson>',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('int32'),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.NamespacedType(['charmie_interfaces', 'msg'], 'DetectedPerson')),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.num_person = kwargs.get('num_person', int())
        self.persons = kwargs.get('persons', [])

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.num_person != other.num_person:
            return False
        if self.persons != other.persons:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @property
    def num_person(self):
        """Message field 'num_person'."""
        return self._num_person

    @num_person.setter
    def num_person(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'num_person' field must be of type 'int'"
            assert value >= -2147483648 and value < 2147483648, \
                "The 'num_person' field must be an integer in [-2147483648, 2147483647]"
        self._num_person = value

    @property
    def persons(self):
        """Message field 'persons'."""
        return self._persons

    @persons.setter
    def persons(self, value):
        if __debug__:
            from charmie_interfaces.msg import DetectedPerson
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, DetectedPerson) for v in value) and
                 True), \
                "The 'persons' field must be a set or sequence and each value of type 'DetectedPerson'"
        self._persons = value
