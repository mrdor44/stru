from .exceptions import (DependencyInvalidValueException, DependencyNoneException, DependencyNotInClassException,
                         UnsupportedOperationException)

import struct

from ..utils import str2bytes, bytes2str

BITS_PER_BYTE = 8


# noinspection PyUnusedLocal
# This is a dummy function
def dummy_callable(*args, **kwargs):
    pass


class Field(object):
    def __init__(self):
        self._endianess = ''

    @property
    def endianess(self):
        return self._endianess

    @endianess.setter
    def endianess(self, value):
        self._endianess = value
        self._after_set_endianess(value)

    def __len__(self):
        """
        Return the static length of the field (regardless of the containing object)
        """
        raise NotImplementedError()

    def dynamic_length(self, obj):
        """
        Return the dynamic length of the field (depending on the containing object)
        :param obj: The object containing the field
        """
        raise NotImplementedError()

    def validate_value(self, obj, value, field_name):
        """
        Validates that a value can be assigned to this field. If not, raises some kind of exception.
        :param obj: The object whose field is assigned to
        :param value: The value assigned
        :param field_name: The field name assigned to
        """
        raise NotImplementedError()

    def pack(self, value, source_obj):
        """
        Packs this field to a buffer
        :param value: The value this field should be packed with
        :param source_obj: The object that contains this field
        """
        raise NotImplementedError()

    def unpack(self, input_stream, target_cls, other_fields):
        """
        Unpack this field from a buffer
        :param input_stream: The stream to read from. Must have a read(amount) function.
        :param target_cls: The class that will be created with this field
        :param other_fields: A dict of other fields that were previously unpacked with this stream
        """
        raise NotImplementedError()

    def _after_set_endianess(self, value):
        pass


# noinspection PyAbstractClass
# This is an abstract class
class PrimitiveField(Field):
    """
    Base class for fields that are automatically supported by the struct module
    """

    def __init__(self, format_string):
        super(PrimitiveField, self).__init__()
        self._format = format_string

    @property
    def format_string(self):
        return self.endianess + self._format

    @property
    def default(self):
        return self._default

    def __len__(self):
        return struct.calcsize(self.format_string)

    def dynamic_length(self, obj):
        return len(self)

    def __call__(self, default=None):
        """
        Used to set field attributes. Supported attributes:
        * default
        EXAMPLE:
            version = FieldType.DWORD(default=2)
        :param default: A default value that will be assigned to this field
        :return: self
        """
        if default is not None:
            self._default = default

        return self

    def __getitem__(self, length):
        """
        Creates an array of this field type.
        EXAMPLE:
            values = FieldType.DWORD[10]
        :param length: The length of the array to create
        """
        return PrimitivesArrayField(length, self)

    def pack(self, value, source_obj):
        return struct.pack(self.format_string, value)

    def unpack(self, buf, target_cls, other_fields):
        value, = struct.unpack(self.format_string, buf.read(len(self)))
        return value


# noinspection PyAbstractClass
# This is an abstract class
class NonPrimitiveField(Field):
    def __init__(self):
        super(NonPrimitiveField, self).__init__()

    @property
    def default(self):
        return self._default

    def __len__(self):
        raise UnsupportedOperationException('len() unsupported for non-primitive type {}'.format(type(self).__name__))

    def __getitem__(self, length):
        """
        Creates an array of this field type.
        :param length: The length of the array to create
        """
        return NonPrimitivesArrayField(length, self)

    def __call__(self, default=None):
        if default is not None:
            self._default = default

        return self


class NumericField(PrimitiveField):
    def __init__(self, format_string):
        super(NumericField, self).__init__(format_string)
        assert len(format_string) == 1

    @property
    def upper_limit(self):
        return 2 ** self._value_bits

    @property
    def max(self):
        return self.upper_limit - 1

    @property
    def lower_limit(self):
        return self.min - 1

    @property
    def min(self):
        raise NotImplementedError()

    def validate_value(self, obj, value, field_name):
        if value is None:
            return
        if not isinstance(value, (int, float)):
            raise TypeError(f'Expected int or float for {field_name}, '
                            f'got {value!r} of type {type(value)}')
        if value > self.max:
            raise ValueError('Value {value} too large! {field}.max = {max}'
                             .format(value=value, field=field_name, max=self.max))
        if value < self.min:
            raise ValueError('Value {value} too small! {field}.min = {min}'
                             .format(value=value, field=field_name, min=self.min))

    @property
    def _value_bits(self):
        raise NotImplementedError()


class SignedNumericField(NumericField):
    @property
    def _value_bits(self):
        return (len(self) * BITS_PER_BYTE) - 1

    @property
    def min(self):
        return -(2 ** self._value_bits)


class UnsignedNumericField(NumericField):
    @property
    def _value_bits(self):
        return len(self) * BITS_PER_BYTE

    @property
    def min(self):
        return 0


class StringField(PrimitiveField):
    def validate_value(self, obj, value, field_name):
        if value is None:
            return
        if not isinstance(value, str):
            raise TypeError(f'Expected str for {field_name}, '
                            f'got {value!r} of type {type(value)}')
        if len(value) > len(self):
            raise ValueError('String "{value}" too long! len({field}) = {max}'
                             .format(value=value, field=field_name, max=len(self)))

    def __getitem__(self, num):
        # __getitem__ can be called upon a StringField to create a string with longer length
        # __getitem__ is not supported on strings longer than one, as we don't support arrays of strings
        # 2 = 1 for endianess, 1 for 's'
        if len(list(filter(lambda c: c not in '@!=<>', self.format_string))) == 1:
            return StringField('{:d}s'.format(num))
        raise NotImplementedError('Arrays of strings not implemented')

    def pack(self, value, source_obj):
        assert isinstance(value, str)
        return super().pack(str2bytes(value), source_obj)

    def unpack(self, buf, target_cls, other_fields):
        # struct.unpack() doesnt stop unpacking on null terminator - it will give us the null terminator as well
        # so we trim it
        return bytes2str(super(StringField, self).unpack(buf, target_cls, other_fields).split(b'\x00', 1)[0])


# noinspection PyAbstractClass
# This is an abstract class
class ArrayField(Field):
    @property
    def count(self):
        raise NotImplementedError()

    @property
    def base(self):
        raise NotImplementedError()

    def validate_value(self, obj, values, field_name):
        if values is None:
            return
        if len(values) != self.count:
            raise ValueError('Array is assigned {num} values! {field}.count = {count}'
                             .format(num=len(values), field=field_name, count=self.count))
        for index, value in enumerate(values):
            self.base.validate_value(obj, value, '{}[{}]'.format(field_name, index))

    def __getitem__(self, num):
        raise NotImplementedError('Multidimensional arrays not implemented')


class PrimitivesArrayField(PrimitiveField, ArrayField):
    def __init__(self, count, base_field_obj):
        # When instantiating an array field obj, there's no endianess yet
        super(PrimitivesArrayField, self).__init__('{:d}{}'.format(count, base_field_obj.format_string))
        self.endianess = base_field_obj.endianess
        self._count = count
        self._base_field_obj = base_field_obj

    @property
    def count(self):
        return self._count

    @property
    def base(self):
        return self._base_field_obj

    def __getitem__(self, num):
        raise NotImplementedError('Multidimensional arrays not implemented')

    def pack(self, values, source_obj):
        return struct.pack(self.format_string, *values)

    def unpack(self, buf, target_cls, other_fields):
        return list(struct.unpack(self.format_string, buf.read(struct.calcsize(self.format_string))))


class NonPrimitivesArrayField(NonPrimitiveField, ArrayField):
    def __init__(self, count, base_field_obj):
        super(NonPrimitivesArrayField, self).__init__()
        self._count = count
        self._base_field_obj = base_field_obj

    @property
    def count(self):
        return self._count

    @property
    def base(self):
        return self._base_field_obj

    def __len__(self):
        return self.count * len(self.base)

    def dynamic_length(self, obj):
        return self.count * self.base.dynamic_length(obj)

    def pack(self, values, source_obj):
        return ''.join(self._base_field_obj.pack(value, source_obj) for value in values)

    def unpack(self, buf, target_cls, other_fields):
        # It looks like unpack_async in purpose, as it is the same code (with or without yields)
        values = []
        for _ in range(self.count):
            value = self.base.unpack(buf, target_cls, other_fields)
            values.append(value)
        return values


class CharArrayField(PrimitivesArrayField):
    def pack(self, values, source_obj):
        if isinstance(values, str):
            # Char can be assigned with str only, but struct module assumes
            # it is of bytes type
            values = list(map(str2bytes, values))
        elif isinstance(values, list):
            assert all(isinstance(e, str) for e in values)
            values = list(map(str2bytes, values))
        return super().pack(values, source_obj)

    def unpack(self, buf, target_cls, other_fields):
        value = super().unpack(buf, target_cls, other_fields)
        assert isinstance(value, list)
        assert all(isinstance(e, bytes) for e in value)
        value = list(map(bytes2str, value))
        return value


class EmbeddedStructField(NonPrimitiveField):
    def __init__(self, struct_cls):
        super(EmbeddedStructField, self).__init__()
        self._base_struct = struct_cls

    @property
    def base(self):
        return self._base_struct

    def __len__(self):
        return len(self.base)

    def dynamic_length(self, obj):
        return len(self.base)

    def __getitem__(self, item):
        raise NotImplementedError('Arrays of embedded structs are currently not supported!')

    def validate_value(self, obj, value, field_name):
        if value is None:
            return
        if not isinstance(value, self.base):
            raise TypeError('{} is of type {}. Got {}'.format(field_name, self.base.__name__, type(value).__name__))

    def pack(self, value, source_obj):
        return value.pack()

    def unpack(self, buf, target_cls, other_fields):
        return self.base.unpack(buf)


# noinspection PyProtectedMember
# Accessing type(obj)._fields
class UnionField(NonPrimitiveField):
    def __init__(self, selector_field_obj, options):
        super(UnionField, self).__init__()
        self._selector_field_obj = selector_field_obj
        self._options = options

    def __getitem__(self, selector_value):
        if selector_value is None:
            raise DependencyNoneException('Selector is None')
        value = self._options.get(selector_value, None)
        if value is None:
            raise DependencyInvalidValueException('No option defined for selector value {}'.format(selector_value))
        return value

    def dynamic_length(self, obj):
        selector_value = self._get_selector_value(obj)
        return self[selector_value].dynamic_length(obj)

    def validate_value(self, obj, value, field_name):
        if value is None:
            return
        selector_value = self._get_selector_value(obj)
        return self[selector_value].validate_value(obj, value, '{}[{}]'.format(field_name, selector_value))

    def pack(self, value, source_obj):
        selector_value = self._get_selector_value(source_obj)
        return self[selector_value].pack(value, source_obj)

    def unpack(self, buf, target_cls, other_fields):
        selector_value = other_fields[self._get_selector_name(target_cls)]
        return self[selector_value].unpack(buf, target_cls, other_fields)

    def _get_selector_name(self, cls):
        selector_name = cls._fields.get(self._selector_field_obj, None)
        if selector_name is None:
            raise DependencyNotInClassException('Selector field does not exist')
        return selector_name

    def _get_selector_value(self, source_obj):
        return getattr(source_obj, self._get_selector_name(type(source_obj)))

    def _after_set_endianess(self, value):
        for field_obj in self._options.values():
            field_obj.endianess = value


# noinspection PyProtectedMember
# Accessing type(obj)._fields
class BufferField(NonPrimitiveField):
    def __init__(self, length_field_obj):
        super(BufferField, self).__init__()
        self._length_field_obj = length_field_obj

    def dynamic_length(self, obj):
        return self._get_length_field_value(obj)

    def validate_value(self, obj, value, field_name):
        if value is None:
            return
        length = self._get_length_field_value(obj)
        if not isinstance(value, bytes):
            raise TypeError('Expected bytes, got: {}'.format(type(value)))
        if len(value) > length:
            raise ValueError('Buffer "{value}" too long! len({field}) = {max}'
                             .format(value=value, field=field_name, max=length))

    def pack(self, value: bytes, source_obj):
        # When packing and unpacking, we use PrimitiveField to avoid the additional processing StringField does
        length = self._get_length_field_value(source_obj)
        return StringField('{:d}s'.format(length)).pack(bytes2str(value), source_obj)

    def unpack(self, buf, target_cls, other_fields):
        length = self._validate_length_value(other_fields[self._get_length_field_name(target_cls)])
        return PrimitiveField('{:d}s'.format(length)).unpack(buf, target_cls, other_fields)

    def _get_length_field_name(self, cls):
        length_field_name = cls._fields.get(self._length_field_obj, None)
        if length_field_name is None:
            raise DependencyNotInClassException('Length field does not exist')
        return length_field_name

    def _get_length_field_value(self, source_obj):
        return self._validate_length_value(getattr(source_obj, self._get_length_field_name(type(source_obj))))

    @staticmethod
    def _validate_length_value(length):
        if length is None:
            raise DependencyNoneException('Length has no value')
        if length < 0:
            raise DependencyInvalidValueException('Length {} is invalid'.format(length))
        return length


class SequenceField(NonPrimitiveField):
    def __init__(self, base_field_obj):
        super(SequenceField, self).__init__()
        self._base_field_obj = base_field_obj

    @property
    def count_format_string(self):
        return '{}{}'.format(self._endianess, 'H')

    @property
    def endianess(self):
        return self._endianess

    @endianess.setter
    def endianess(self, value):
        self._endianess = value
        self._after_set_endianess(value)
        self._base_field_obj.endianess = value

    def validate_value(self, obj, values, field_name):
        if values is None:
            return

        for index, value in enumerate(values):
            self._base_field_obj.validate_value(obj, value, '{}[{}]'.format(field_name, index))

        self._base_field_obj.endianess = self.endianess

    def pack(self, values, source_obj):
        return struct.pack(self.count_format_string, len(values)) + b''.join(
            self._base_field_obj.pack(value, source_obj) for value in values)

    def unpack(self, buf, target_cls, other_fields):
        values = []

        read_size = struct.calcsize(self.count_format_string)
        count = struct.unpack(self.count_format_string, buf.read(struct.calcsize(self.count_format_string)))[0]

        for _ in range(count):
            value = self._base_field_obj.unpack(buf, target_cls, other_fields)
            values.append(value)
        return values


class BoolField(PrimitiveField):
    def __init__(self, format_string):
        assert format_string == '?'
        super(BoolField, self).__init__(format_string)

    def validate_value(self, obj, value, field_name):
        if value not in [None, True, False]:
            raise ValueError('Tried to assign {} to boolean field {}'.format(value, field_name))


class CharField(PrimitiveField):
    def __init__(self, format_string):
        assert format_string == 'c'
        super(CharField, self).__init__(format_string)

    @property
    def max(self):
        return chr(255)

    @property
    def min(self):
        return chr(0)

    def __getitem__(self, length):
        """
        Creates an array of chars.
        EXAMPLE:
            values = FieldType.Char[10]
        :param length: The length of the array to create
        """
        return CharArrayField(length, self)

    def validate_value(self, obj, value, field_name):
        if value is None:
            return
        if not isinstance(value, str):
            raise ValueError('Value {} is not a string'.format(value))
        if len(value) != 1:
            raise ValueError('Expected a 1-length string (a character). Got a string of length {}'.format(len(value)))

    def pack(self, value, source_obj):
        if isinstance(value, str):
            value = str2bytes(value)
        return struct.pack(self.format_string, value)

    def unpack(self, buf, target_cls, other_fields):
        value, = struct.unpack(self.format_string, buf.read(len(self)))
        return bytes2str(value)


class NoValueField(PrimitiveField):
    def __init__(self, format_string):
        super(NoValueField, self).__init__(format_string)

    def __getitem__(self, item):
        raise NotImplementedError('Arrays of PadBytes are not supported')

    def validate_value(self, obj, value, field_name):
        if value is not None:
            raise ValueError("Field {} can't be assigned a value. Tried to assign {}".format(field_name, value))

    def pack(self, value, source_obj):
        assert value is None
        return struct.pack(self.format_string)

    def unpack(self, buf, target_cls, other_fields):
        t = struct.unpack(self.format_string, buf.read(struct.calcsize(self.format_string)))
        assert len(t) == 0
        return None
