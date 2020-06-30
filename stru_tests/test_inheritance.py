from stru import Struct, Endianess, FieldType
from stru_tests.struct_test_case import StructTestCase, const

import unittest


class Base1(Struct):
    _endianess = Endianess.BigEndian
    x = FieldType.UnsignedLong
    a = FieldType.Char
    e = FieldType.BYTE(default=5)


class Base2(Base1):
    y = FieldType.Long
    b = FieldType.PadByte


class Base3(Base2):
    w = FieldType.String[4]
    d = FieldType.Struct(Base2)


class Derived(Base3):
    z = FieldType.Bool
    c = FieldType.SignedWORD[2]


class InheritanceTests(StructTestCase, unittest.TestCase):
    def create_target(self):
        inner = Base2(x=3, a='b', y=4)
        inner_buff = b'\x00\x00\x00\x03' b'b' b'\x05' b'\x00\x00\x00\x04' b'\x00'

        obj = Derived(x=1, a='a', y=2, w='abcd', d=inner, z=True, c=[5, 6])
        buff = (b'\x00\x00\x00\x01' b'a' b'\x05' b'\x00\x00\x00\x02' b'\x00' b'abcd'
                + inner_buff + b'\x01' b'\x00\x05\x00\x06')

        return obj, buff

    def get_fields(self):
        return [(Derived.x, const.DWORD),
                (Derived.a, const.Char),
                (Derived.e, const.BYTE),
                (Derived.y, const.SignedDWORD),
                (Derived.d.base.x, const.DWORD),
                (Derived.d.base.a, const.Char),
                (Derived.d.base.e, const.BYTE),
                (Derived.d.base.y, const.SignedDWORD),
                (Derived.c.base, const.SignedWORD)]

    def test_lengths(self):
        self.assertEqual(len(Derived.x), 4)
        self.assertEqual(len(Derived.a), 1)
        self.assertEqual(len(Derived.e), 1)
        self.assertEqual(len(Derived.y), 4)
        self.assertEqual(len(Derived.b), 1)
        self.assertEqual(len(Derived.w), 4)
        self.assertEqual(len(Derived.d.base.x), 4)
        self.assertEqual(len(Derived.d.base.a), 1)
        self.assertEqual(len(Derived.d.base.e), 1)
        self.assertEqual(len(Derived.d.base.y), 4)
        self.assertEqual(len(Derived.d.base.b), 1)
        self.assertEqual(len(Derived.z), 1)
        self.assertEqual(len(Derived.c.base), 2)
        self.assertEqual(len(Derived), 31)
        self.assertEqual(len(self.obj), 31)


if __name__ == '__main__':
    unittest.main()
