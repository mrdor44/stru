from stru import FieldType, Struct, Endianess
from stru_tests.struct_test_case import StructTestCase, const

import unittest
import struct


class GiantStruct(Struct):
    _endianess = Endianess.LittleEndian
    char = FieldType.Char
    ushort = FieldType.UnsignedShort
    i = FieldType.Int
    boo = FieldType.Bool
    short = FieldType.Short
    sbyte = FieldType.SignedBYTE
    pad1 = FieldType.PadByte
    byt = FieldType.BYTE
    lonlon = FieldType.LongLong
    uint = FieldType.UnsignedInt
    lon = FieldType.Long
    ulong = FieldType.UnsignedLong
    dqword = FieldType.SignedQWORD
    flt = FieldType.Float
    dbl = FieldType.Double
    sword = FieldType.SignedWORD
    ulonglong = FieldType.UnsignedLongLong
    word = FieldType.WORD
    sdword = FieldType.SignedDWORD
    dword = FieldType.DWORD
    pad2 = FieldType.PadByte
    qword = FieldType.QWORD


class SupportedTypesTest(StructTestCase, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.unsigned_1_byte = [GiantStruct.byt]
        cls.signed_1_byte = [GiantStruct.sbyte]
        cls.signed_2_bytes = [GiantStruct.short, GiantStruct.sword]
        cls.unsigned_2_bytes = [GiantStruct.ushort, GiantStruct.word]
        cls.signed_4_bytes = [GiantStruct.i, GiantStruct.lon, GiantStruct.flt, GiantStruct.sdword]
        cls.unsigned_4_bytes = [GiantStruct.uint, GiantStruct.ulong, GiantStruct.dword]
        cls.signed_8_bytes = [GiantStruct.lonlon, GiantStruct.dqword, GiantStruct.dbl]
        cls.unsigned_8_bytes = [GiantStruct.ulonglong, GiantStruct.qword]

    def create_target(self):
        obj = GiantStruct(char='a',
                          ushort=1,
                          i=2,
                          boo=False,
                          short=3,
                          sbyte=4,
                          byt=5,
                          lonlon=6,
                          uint=7,
                          lon=8,
                          ulong=9,
                          dqword=10,
                          flt=11.5,
                          dbl=12.5,
                          sword=13,
                          ulonglong=14,
                          word=15,
                          sdword=16,
                          dword=17,
                          qword=19)
        buff = struct.pack('<cHi?hbxBqIlLqfdhQHlLxQ',
                           obj.char,
                           obj.ushort,
                           obj.i,
                           obj.boo,
                           obj.short,
                           obj.sbyte,
                           obj.byt,
                           obj.lonlon,
                           obj.uint,
                           obj.lon,
                           obj.ulong,
                           obj.dqword,
                           obj.flt,
                           obj.dbl,
                           obj.sword,
                           obj.ulonglong,
                           obj.word,
                           obj.sdword,
                           obj.dword,
                           obj.qword)
        return obj, buff

    # noinspection PyTypeChecker
    def get_fields(self):
        return ([(GiantStruct.char, const.Char)] +
                [(field, const.BYTE) for field in self.unsigned_1_byte] +
                [(field, const.SignedBYTE) for field in self.signed_1_byte] +
                [(field, const.WORD) for field in self.unsigned_2_bytes] +
                [(field, const.SignedWORD) for field in self.signed_2_bytes] +
                [(field, const.DWORD) for field in self.unsigned_4_bytes] +
                [(field, const.SignedDWORD) for field in self.signed_4_bytes] +
                [(field, const.QWORD) for field in self.unsigned_8_bytes] +
                [(field, const.SignedQWORD) for field in self.signed_8_bytes])

    def test_lengths(self):
        for field in self.signed_1_byte + self.unsigned_1_byte:
            self.assertEqual(len(field), 1)
        for field in self.signed_2_bytes + self.unsigned_2_bytes:
            self.assertEqual(len(field), 2)
        for field in self.signed_4_bytes + self.unsigned_4_bytes:
            self.assertEqual(len(field), 4)
        for field in self.signed_8_bytes + self.unsigned_8_bytes:
            self.assertEqual(len(field), 8)
        self.assertEqual(len(GiantStruct), 82)
        self.assertEqual(len(self.obj), 82)

    def test_invalid_value_assignments(self):
        assignments = {
            'char': [14, 'ab', [], ''],
            'ushort': ['a', [], ''],
            'boo': ['a', 14, 'abcd', [], ''],
            'pad1': [0, [], ''],
            'pad2': [0, [], ''],
        }

        numeric_assignments = [
            'i',
            'short',
            'sbyte',
            'byt',
            'lonlon',
            'uint',
            'lon',
            'ulong',
            'dqword',
            'flt',
            'dbl',
            'sword',
            'ulonglong',
            'word',
            'sdword',
            'dword',
            'qword',
        ]

        for field_name, values in assignments.iteritems():
            for value in values:
                with self.assertRaises(ValueError):
                    setattr(self.obj, field_name, value)

        for field_name in numeric_assignments:
            field_obj = getattr(GiantStruct, field_name)
            values = [field_obj.max * 2, field_obj.min - 3, field_obj.upper_limit, field_obj.lower_limit]
            for value in values:
                with self.assertRaises(ValueError):
                    setattr(self.obj, field_name, value)

        for field_name in assignments.keys() + numeric_assignments:
            setattr(self.obj, field_name, None)

    def test_fields_correct_values(self):
        self.assertEqual(self.obj.char, 'a')
        self.assertEqual(self.obj.ushort, 1)
        self.assertEqual(self.obj.i, 2)
        self.assertEqual(self.obj.boo, False)
        self.assertEqual(self.obj.short, 3)
        self.assertEqual(self.obj.sbyte, 4)
        self.assertEqual(self.obj.byt, 5)
        self.assertEqual(self.obj.lonlon, 6)
        self.assertEqual(self.obj.uint, 7)
        self.assertEqual(self.obj.lon, 8)
        self.assertEqual(self.obj.ulong, 9)
        self.assertEqual(self.obj.dqword, 10)
        self.assertEqual(self.obj.flt, 11.5)
        self.assertEqual(self.obj.dbl, 12.5)
        self.assertEqual(self.obj.sword, 13)
        self.assertEqual(self.obj.ulonglong, 14)
        self.assertEqual(self.obj.word, 15)
        self.assertEqual(self.obj.sdword, 16)
        self.assertEqual(self.obj.dword, 17)
        self.assertEqual(self.obj.qword, 19)
        self.assertIsNone(self.obj.pad1)
        self.assertIsNone(self.obj.pad2)


if __name__ == '__main__':
    unittest.main()
