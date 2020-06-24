"""
Enhanced Struct is a package that allows defining classes as C-style structs.
To do this, one needs only to inherit from Struct.
After that, you can define the fields that your class will have, and their appropriate type.

EXAMPLE:
    >>> class Point(Struct):
    ...     _endianess = Endianess.LittleEndian
    ...     x = FieldType.WORD
    ...     y = FieldType.WORD

The _endianess field tells Struct the endianess of the structured data (little endian, big endian, etc.).
With Point defined as above, you automagically get a few features out-of-the-box:
 1. pack() and unpack() methods
 2. max, min, upper_limit and lower_limit bounds on each field
 3. length of each field in bytes
 4. length of the whole structure in bytes
 5. value-assignment checks when assigning values to fields (assigning None is permitted)
 6. Equality operators on structs that check field-by-field

EXAMPLE:
    >>> p = Point(x=1, y=2)
    >>> assert p.pack() == '\x01\x00\x02\x00'   # Automatic .pack() method
    >>> assert Point.x.max == 65535             # This is the maximal allowed value for a WORD field
    >>> assert Point.y.min == 0                 # This is the minimal allowed value for a WORD field
    >>> assert Point.x.upper_limit == 65536     # This is upper (non-inclusive) limit for a WORD field
    >>> assert Point.y.lower_limit == -1        # This is lower (non-inclusive) limit for a WORD field
    >>> p2 = Point.unpack('\x01\x00\x02\x00')   # Automatic .unpack() method
    >>> assert p2.x == 1 and p2.y == 2
    >>> assert p2 == p and not (p2 != p)        # Automatic equality/inequality operators
    >>> assert len(Point.x) == 2                # len() of a field gives its size in bytes
    >>> assert len(Point) == len(p) == 4        # len() of the class itself or an instance
    >>> p.x = Point.x.upper_limit               # Setting with a value too large raises a ValueError
    ValueError
    >>> p.x = Point.x.lower_limit               # Setting with a value too small raises a ValueError
    ValueError

The supported values for the _endianess field are as seen in class Endianess.
The supported field types are: [
    FieldType.PadByte,
    FieldType.Char,
    FieldType.Bool,
    FieldType.Short,
    FieldType.UnsignedShort,
    FieldType.Int,
    FieldType.UnsignedInt,
    FieldType.Long,
    FieldType.UnsignedLong,
    FieldType.LongLong,
    FieldType.UnsignedLongLong,
    FieldType.BYTE,
    FieldType.WORD,
    FieldType.DWORD,
    FieldType.QWORD,
    FieldType.SignedBYTE,
    FieldType.SignedWORD,
    FieldType.SignedDWORD,
    FieldType.SignedQWORD,
    FieldType.Float,
    FieldType.Double,
    FieldType.String
]

Strings
-------
You can specify constant-length string fields easily.
EXAMPLE:
    >>> class Person(Struct):
    ...     name = FieldType.String[10](default="John Doe")

Strings support everything other fields do (except max, min and such, of course).

    >>> assert len(Person.name) == 10
    >>> assert len(Person(name='mr')) == 10

CAUTION:
    Don't assign values with null-terminator characters ('\x00') to strings in EnhancedStructs, as they will not be
    handled well. They will truncate and may mess up the entire parsing.

Arrays
------
You can specify constant-length array fields. They support len() and other attributes as with other fields.
They support two more features:
 1. len() gives the array size in bytes. If you want the number of elements, use .count
 2. You can access the base type contained in the array, by using .base

EXAMPLE:
    >>> class Datagram(Struct):
    ...     data = FieldType.WORD[8]

    >>> d = Datagram(data=[1, 2, 3, 4, 5, 6, 7, 8])
    >>> assert len(d) == len(Datagram.data) == 16     # len() gives the size in bytes, as with all other fields
    >>> assert Datagram.data.count == 8               # count gives the number of elements
    >>> assert Datagram.data.base.max == 65535        # base gives the base element (WORD, in our case)

Setting array fields performs several safety checks:
 1. Setting a too-long or too-short array will raise an exception
 2. Setting an array with too big or too small values will raise an exception

NOTE: Setting an invalid value to an already existing array will succeed (it will fail in pack())
NOTE: Multidimensional arrays and arrays of strings are not supported
NOTE: Arrays of PadByte isn't supported

Embedded Structs
----------------
You can embed EnhancedStructs inside other EnhancedStructs.
Embedded structs allow getting the base struct using .base

EXAMPLE:
    >>> class MyPoint(Struct):
    ...     _endianess = Endianess.BigEndian
    ...     point = FieldType.Struct(Point)

    >>> p = MyPoint(point=Point(x=1, y=2))
    >>> assert p.pack() == Point(x=1, y=2).pack()
    >>> assert MyPoint.point.base.x.max == 65535

NOTE: An embedded struct is packed with it's own endianess, NOT the outer struct's endianess

Default Values
--------------
One can specify default values to fields. If an instance doesn't assign value to this field, the default value
takes effect.
You can access a field's default value using .default

EXAMPLE:
    >>> class Packet(Struct):
    ...     __magic__ = FieldType.DWORD(default=0xABCD)

    >>> p = Packet()
    >>> assert p.__magic__ == 0xABCD
    >>> Packet.__magic__.default == 0xABCD
    >>> assert p.pack() == '\xcd\xab\x00\x00'

Once the default value is overridden or deleted, it won't take effect anymore, ever.

NOTE: Default values are not supported for non-primitives, such as EmbeddedStructs, Unions and Buffers

Inheritance
-----------
Struct supports inheritance from other classes that are Struct.
The derived class extends the parent's structure.

EXAMPLE:
    >>> class Point3D(Point):
    ...     z = FieldType.Short

    >>> p = Point3D(x=1, y=2, z=3)
    >>> assert p.pack() == '\x01\x00\x02\x00\x03\x00'
    >>> assert len(Point3D.x) == 2
    >>> assert len(Point3D) == 6

NOTE: You cannot change the base class's endianess. Doing so will cause undefined behavior

Custom Read
-----------
The Struct.unpack() method supports several types of input streams:
 1. A regular string buffer, like used in examples above.
 2. A callable object (or function, of course).
    The first parameter of this callable is the amount of bytes to read.
    If the callable needs more parameters, you can pass them to unpack() and it will transfer them.

EXAMPLE:
    >>> class SpecialSocket(object):
    ...     def read(self, amount_bytes, target, param):
    ...         # Do something
    ...         pass

    >>> special_socket = SpecialSocket()
    >>> p = Point.unpack(special_socket.read, '127.0.0.1', 4000)

SpecialSocket.read() will be called several times, with different amounts each time. However, the target and param
arguments will always be the same ones passed to unpack()

Unions
------
You can define a union field - the field will be one of many options, depending on another field.

EXAMPLE:
    >>> class VersionedPacket(Struct):
    ...     _endianess = Endianess.BigEndian
    ...     version = FieldType.WORD
    ...     data = FieldType.Union(version, {
    ...         1: FieldType.DWORD,
    ...         2: FieldType.Struct(Point)
    ...     })

    >>> vp = VersionedPacket.unpack('\x00\x01\xab\xcd\x12\x34')
    >>> assert vp.data == 0xABCD1234
    >>> assert VersionedPacket.data[1].max == Packet.__magic__.max

When packing and unpacking the struct, the union will choose the right option based on the selector.

NOTE: Setting default values to fields inside a union will not do anything

Buffers
-------
You can define a field to be a variable-length buffer, which its length is defined by another field in the struct.

EXAMPLE:
    >>> class Buffered(Struct):
    ...     _endianess = Endianess.BigEndian
    ...     length = FieldType.WORD
    ...     data = FieldType.Buffer(length)

    >>> b = Buffered(length=2, data='AB')
    >>> assert b.pack() == '\x00\x02AB'
    >>> assert Buffered.unpack('\x00\x02AB').data == b.data
    >>> assert len(b) == 4

Deferred Unpacking
------------------
EnhancedStructs support unpacking from an asynchronous source.

EXAMPLE:
    >>> class SpecialAsyncSocket(object):
    ...     @coroutine
    ...     def read(self, amount_bytes, target, param):
    ...         # Do something
    ...         pass

    >>> special_socket = SpecialAsyncSocket()
    >>> s = yield Point.unpack_async(special_socket.read, '127.0.0.1', 4000)


Dynamic Length
--------------
EnhancedStructs support dynamic length calculation:

    >>> class MyStruct(Struct):
    ...     selector = FieldType.DWORD
    ...     data = FieldType.Union(selector, {
    ...         1: FieldType.DWORD
    ...         2: FieldType.WORD
    ...     })

    >>> len(MyStruct) # throws an exception, as the union is not determined
    >>> m = MyStruct(selector=1, data=2)
    >>> assert len(m) == 8  # Now we know the union's length, so we can tell the struct's length

Thread-Safety
-------------
Struct is entirely thread-safe, EXCEPT for the creation of classes and their fields.
For 100% thread-safety, you can supply a lock that will be used for classes creation.
The supplied lock needs to have an .acquire() method and a .release() method.

EXAMPLE:
    >>> class MyLovelyLock(object):
    ...     def acquire(self):
    ...         pass
    ...     def release(self):
    ...         pass


    >>> lock = MyLovelyLock()
    >>> old_lock = set_global_lock(lock)          # From now on, Struct is entirely thread-safe

Before & After
--------------
You can specify an action to perform before/after unpacking/packing a field. In this action, you can verify an
assertion or alter the packed/unpacked value.

EXAMPLE:
    >>> class Altered(object):
    ...     x = FieldType.WORD(before_pack=..., before_unpack=..., after_pack=..., after_unpack=...)

Each of these arguments is optional. You can pass none of them, all of them, or some of them.

* before_pack will be given the value to pack. It can change the packed value by returning a new value.
* before_unpack will be given the buffer to unpack from. It can change the buffer by returning a new buffer.
* after_pack will be given the packed buffer. It can change the buffer by returning a new buffer.
* after_unpack will be given the unpacked value. It can change the value by returning a new value.

It's safe to return None from each of these handlers. In case of None, the original parameter given to the handler will
be used (the None will be ignored).

NOTE: Setting these handlers is possible only in field types that support the "default" parameter.

Notes
-----
* Inheriting Struct causes the addition of several class-level fields. Pay attention not to override them
  with your own fields. The added fields are:
    _endianess, _fields, _defaults
* Pascal strings are not supported
"""
from stru.field import (UnsupportedOperationException, DependencyNotInClassException,
                        DependencyInvalidValueException, DependencyNoneException)
from stru.field_type import FieldType
from stru.enhanced_struct import Endianess
from stru.stru_struct import Struct

__all__ = ['field', 'field_type', 'enhanced_struct']
