from stru.enhanced_struct import MissingEndianessException
from stru.field.field import Field
from stru.meta_struct import MetaStruct
from stru.unpack_stream import UnpackStream


class Struct(metaclass=MetaStruct):
    _endianess = None
    _fields = None
    _defaults = None

    def __init__(self, **kwargs):
        if self._endianess is None:
            raise MissingEndianessException("Can't create a Struct without endianess")

        for field_name in type(self)._fields.values():
            setattr(self, field_name, None)
        for k, v in type(self)._defaults:
            setattr(self, k, v)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def _set_attributes_by_order(self, attributes):
        for k, v in sorted(attributes):
            setattr(self, k, v)

    def __len__(self):
        return sum(field_obj.dynamic_length(self) for field_obj in type(self)._fields.keys())

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return all(getattr(self, field_name) == getattr(other, field_name)
                   for field_name in type(self)._fields.values())

    def __ne__(self, other):
        return not (self == other)

    def pack(self):
        struct_parts = []

        for field_obj, field_name in type(self)._fields.items():
            packed_value = field_obj.pack(getattr(self, field_name), self)
            struct_parts.append(packed_value)

        return b''.join(struct_parts)

    @classmethod
    def unpack(cls, input_stream, *args, **kwargs):
        input_stream = UnpackStream.create(input_stream, *args, **kwargs)
        fields_dict = {}
        for field_obj, field_name in cls._fields.items():
            value = field_obj.unpack(input_stream, cls, fields_dict)
            fields_dict.update({field_name: value})
        return cls(**fields_dict)

    def __setattr__(self, key, value):
        field_obj = getattr(type(self), key)
        if isinstance(field_obj, Field):
            field_obj.validate_value(self, value, '{}.{}'.format(type(self).__name__, key))
        return super(Struct, self).__setattr__(key, value)

    def __delattr__(self, item):
        super(Struct, self).__delattr__(item)
        setattr(self, item, None)
