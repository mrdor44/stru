from stru import Endianess, FieldType
from stru.stru_struct import Struct
from stru_tests.struct_test_case import StructTestCase, const

import unittest


class Point(Struct):
    _endianess = Endianess.LittleEndian
    x = FieldType.WORD(default=2)
    y = FieldType.WORD(default=3)


class AllDefault(Struct):
    _endianess = Endianess.BigEndian
    a = FieldType.Short(default=-10)
    b = FieldType.UnsignedShort(default=20)
    c = FieldType.Bool(default=True)
    d = FieldType.String[8](default='bla')
    e = FieldType.Char(default='a')
    f = FieldType.Long[3](default=[1, 2, 3])
    g = FieldType.Struct(Point)


class DefaultsTest(StructTestCase, unittest.TestCase):
    def create_target(self):
        obj = AllDefault(g=Point())
        buff = ('\xff\xf6' '\x00\x14' '\x01' 'bla\x00\x00\x00\x00\x00' 'a' '\x00\x00\x00\x01' '\x00\x00\x00\x02'
                '\x00\x00\x00\x03' '\x02\x00\x03\x00')
        return obj, buff

    def get_fields(self):
        return [(AllDefault.a, const.SignedWORD),
                (AllDefault.b, const.WORD),
                (AllDefault.e, const.Char),
                (AllDefault.f.base, const.SignedDWORD),
                (AllDefault.g.base.x, const.WORD),
                (AllDefault.g.base.y, const.WORD)]

    def test_default_property(self):
        self.assertEqual(AllDefault.a.default, -10)
        self.assertEqual(AllDefault.b.default, 20)
        self.assertEqual(AllDefault.c.default, True)
        self.assertEqual(AllDefault.d.default, 'bla')
        self.assertEqual(AllDefault.e.default, 'a')
        self.assertEqual(AllDefault.f.default, [1, 2, 3])
        self.assertEqual(AllDefault.g.base.x.default, 2)
        self.assertEqual(AllDefault.g.base.y.default, 3)

    def test_delete_default(self):
        self.obj.a = 5
        self.assertEqual(self.obj.a, 5)
        del self.obj.a
        self.assertEqual(self.obj.a, None)

    # noinspection PyUnusedLocal
    def test_unsupported(self):
        with self.assertRaises(TypeError):
            class Embedded(Struct):
                a = FieldType.Struct(Point)(default=Point(x=1, y=2))
        with self.assertRaises(TypeError):
            class Union(Struct):
                a = FieldType.DWORD
                b = FieldType.Union(a, {
                    1: FieldType.WORD
                })(default=5)
        with self.assertRaises(TypeError):
            class Buffered(Struct):
                a = FieldType.DWORD
                b = FieldType.Buffer(a)(default=[])
