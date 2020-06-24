import collections
from collections import OrderedDict

from stru.field.field import Field


class DifferentEndianessException(Exception):
    pass


class MetaStruct(type):
    # noinspection PyProtectedMember
    # Accessing base._endianess
    def __init__(cls, name, bases, d):
        super(MetaStruct, cls).__init__(name, bases, d)

        for base in bases:
            if hasattr(base, '_endianess') and base._endianess is not None and cls._endianess != base._endianess:
                raise DifferentEndianessException("{cls.__name__}._endianess='{cls._endianess}', "
                                                  "differs from base {base.__name__}._endianess='{base._endianess}'"
                                                  .format(cls=cls, base=base))

        # If this class inherits another Struct, it will already have these fields set
        # In this case, we need to make a copy of them, to avoid overwriting the parent class' fields
        cls._fields = OrderedDict(cls._fields) if cls._fields is not None else OrderedDict()
        cls._defaults = cls._defaults[:] if cls._defaults is not None else []

        local_fields = [(field_obj, field_name) for field_name, field_obj in d.items()
                        if isinstance(field_obj, Field)]

        # cls._fields is an OrderedDict({field_obj: field_name})
        # cls._defaults is a list([(field_name, default_value)])
        cls._fields.update(local_fields)
        cls._defaults += [(field_name, field_obj.default)
                          for field_obj, field_name in local_fields if hasattr(field_obj, 'default')]

        for field_obj in cls._fields.keys():
            field_obj.endianess = cls._endianess

    @classmethod
    def __prepare__(metacls, name, bases):
        return collections.OrderedDict()

    def __len__(self):
        return sum(map(len, self._fields.keys()))
