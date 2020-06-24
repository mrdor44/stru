from .field import (SignedNumericField, UnsignedNumericField, StringField, EmbeddedStructField, UnionField, BufferField,
                    BoolField, CharField, NoValueField)


# noinspection PyPep8Naming
# We want type names to be uppercase sometimes
class FieldType(object):
    def __getattr__(self, item):
        STRUCT_FORMAT = {
            'PadByte': ('x', NoValueField),
            'Char': ('c', CharField),
            'Bool': ('?', BoolField),
            'Short': ('h', SignedNumericField),
            'UnsignedShort': ('H', UnsignedNumericField),
            'Int': ('i', SignedNumericField),
            'UnsignedInt': ('I', UnsignedNumericField),
            'Long': ('l', SignedNumericField),
            'UnsignedLong': ('L', UnsignedNumericField),
            'LongLong': ('q', SignedNumericField),
            'UnsignedLongLong': ('Q', UnsignedNumericField),
            'BYTE': ('B', UnsignedNumericField),
            'WORD': ('H', UnsignedNumericField),
            'DWORD': ('L', UnsignedNumericField),
            'QWORD': ('Q', UnsignedNumericField),
            'SignedBYTE': ('b', SignedNumericField),
            'SignedWORD': ('h', SignedNumericField),
            'SignedDWORD': ('l', SignedNumericField),
            'SignedQWORD': ('q', SignedNumericField),
            'Float': ('f', SignedNumericField),
            'Double': ('d', SignedNumericField),
            'String': ('s', StringField),
        }
        fmt, cls = STRUCT_FORMAT[item]
        return cls(fmt)

    @staticmethod
    def Struct(struct_cls):
        """
        Define an embedded struct field
        :param struct_cls: The Struct class to embed
        """
        return EmbeddedStructField(struct_cls)

    @staticmethod
    def Union(selector_field_obj, options_dict):
        """
        Define a union field
        :param selector_field_obj: The field to use as a selector
        :param options_dict: A dict with the form {value: field}.
        """
        return UnionField(selector_field_obj, options_dict)

    @staticmethod
    def Buffer(length_field_obj):
        """
        Define a variable-length buffer field
        :param length_field_obj: The field to use as a length indicator
        """
        return BufferField(length_field_obj)


# This allows convenient use of FieldType as a constructor object
FieldType = FieldType()
