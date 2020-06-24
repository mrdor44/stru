from stru import Struct, FieldType, Endianess
from stru_tests.struct_test_case import StructTestCase, const

import unittest


class Inner1(Struct):
    _endianess = Endianess.BigEndian
    a = FieldType.Long
    b = FieldType.Bool


class Inner2(Struct):
    _endianess = Endianess.LittleEndian
    a = FieldType.QWORD
    b = FieldType.String[8]


class Inner3(Struct):
    _endianess = Endianess.Network
    pass


class Inner4(Struct):
    _endianess = Endianess.LittleEndian
    a = FieldType.Struct(Inner1)
    b = FieldType.PadByte


class Inner5(Struct):
    _endianess = Endianess.BigEndian
    a = FieldType.Char
    b = FieldType.Struct(Inner2)


class Inner6(Struct):
    _endianess = Endianess.LittleEndian
    a = FieldType.Bool[2]
    b = FieldType.Struct(Inner5)
    c = FieldType.UnsignedLongLong[3]


class Inner7(Struct):
    _endianess = Endianess.BigEndian
    a = FieldType.Char[4]
    b = FieldType.Struct(Inner6)


class VeryEmbedded(Struct):
    _endianess = Endianess.LittleEndian
    a = FieldType.Struct(Inner4)
    b = FieldType.Struct(Inner7)
    c = FieldType.BYTE[4]
    d = FieldType.Struct(Inner3)


class EmbeddedStructsTests(StructTestCase, unittest.TestCase):
    def create_target(self):
        inner2 = Inner2(a=40, b='wxyzwxyz')
        buff2 = '\x28\x00\x00\x00\x00\x00\x00\x00wxyzwxyz'

        inner5 = Inner5(a='e', b=inner2)
        buff5 = 'e' + buff2

        inner6 = Inner6(a=[True, False], b=inner5, c=[10, 20, 30])
        buff6 = '\x01\x00' + buff5 + chr(10) + '\x00' * 7 + chr(20) + '\x00' * 7 + chr(30) + '\x00' * 7

        inner7 = Inner7(a=['a', 'b', 'c', 'd'], b=inner6)
        buff7 = 'abcd' + buff6

        inner1 = Inner1(a=1, b=False)
        buff1 = '\x00\x00\x00\x01' '\x00'

        inner4 = Inner4(a=inner1)
        buff4 = buff1 + '\x00'

        inner3 = Inner3()
        buff3 = ''

        obj = VeryEmbedded(a=inner4, b=inner7, c=[255, 254, 253, 252], d=inner3)
        buff = buff4 + buff7 + chr(255) + chr(254) + chr(253) + chr(252) + buff3

        return obj, buff

    def get_fields(self):
        return [(VeryEmbedded.a.base.a.base.a, const.SignedDWORD),
                (VeryEmbedded.b.base.a.base, const.Char),
                (VeryEmbedded.b.base.b.base.b.base.a, const.Char),
                (VeryEmbedded.b.base.b.base.b.base.b.base.a, const.QWORD),
                (VeryEmbedded.b.base.b.base.c.base, const.QWORD),
                (VeryEmbedded.c.base, const.BYTE)]

    def test_lengths(self):
        self.assertEqual(len(VeryEmbedded.a), 6)
        self.assertEqual(len(VeryEmbedded.b), 47)
        self.assertEqual(len(VeryEmbedded.d), 0)
        self.assertEqual(len(VeryEmbedded), 57)
        self.assertEqual(len(self.obj), 57)

    def test_invalid_value_assignment(self):
        with self.assertRaises(ValueError):
            self.obj.a.b = 1
        with self.assertRaises(ValueError):
            self.obj.b.b.b.a = const.QWORD.LOWER_LIMIT
        with self.assertRaises(TypeError):
            self.obj.b = Inner3()


if __name__ == '__main__':
    unittest.main()
