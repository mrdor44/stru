import unittest

from stru import FieldType, Endianess
from stru.stru_struct import Struct
from tests.utils import EnhancedStructTestCase, const


class Packet(Struct):
    _endianess = Endianess.Network
    magic = FieldType.DWORD
    data = FieldType.DWORD[20]
    crc = FieldType.WORD


class ArraysTest(EnhancedStructTestCase, unittest.TestCase):
    def create_target(self):
        obj = Packet(magic=0xABCD, data=[0xEF] * Packet.data.count, crc=0x97)
        buff = '\x00\x00\xAB\xCD' + '\x00\x00\x00\xef' * 20 + '\x00\x97'
        return obj, buff

    def get_fields(self):
        return [(Packet.data.base, const.DWORD)]

    def test_lengths(self):
        self.assertEqual(len(Packet.data), 20 * 4)
        self.assertEqual(len(Packet), 4 + 20 * 4 + 2)
        self.assertEqual(len(self.obj), 4 + 20 * 4 + 2)
        self.assertEqual(len(self.obj.data), 20)

    def test_invalid_value_assignments(self):
        with self.assertRaises(ValueError):
            self.obj.data = [1] * 30
        with self.assertRaises(ValueError):
            self.obj.data = [1] * 19
        with self.assertRaises(ValueError):
            self.obj.data = [-1] * 20
        with self.assertRaises(ValueError):
            self.obj.data = [0] * 10 + [18446744073709551616] + [0] * 9

    def test_count(self):
        self.assertEqual(Packet.data.count, 20)

    @unittest.expectedFailure
    def test_invalid_assignment_on_existing_array(self):
        with self.assertRaises(ValueError):
            self.obj.data[0] = 18446744073709551616

    # noinspection PyUnusedLocal
    def test_unsupported_arrays(self):
        with self.assertRaises(NotImplementedError):
            class Multidimensional(Struct):
                a = FieldType.WORD[5][5]
        with self.assertRaises(NotImplementedError):
            class StringArray(Struct):
                a = FieldType.String[10][5]
        with self.assertRaises(NotImplementedError):
            class PadByteArray(Struct):
                a = FieldType.PadByte[5]
        with self.assertRaises(NotImplementedError):
            class EmbeddedStructArray(Struct):
                a = FieldType.Struct(Packet)[5]


class Various(Struct):
    _endianess = Endianess.LittleEndian
    signed = FieldType.SignedWORD[3]
    unsigned = FieldType.WORD[4]
    bools = FieldType.Bool[6]
    chars = FieldType.Char[8]


class VariousArraysTest(EnhancedStructTestCase, unittest.TestCase):
    def create_target(self):
        obj = Various(signed=[1, 2, 3],
                      unsigned=[4, 5, 6, 7],
                      bools=[True, False] * 3,
                      chars=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
        buff = '\x01\x00\x02\x00\x03\x00' '\x04\x00\x05\x00\x06\x00\x07\x00' + '\x01\x00' * 3 + 'abcdefgh'
        return obj, buff

    def get_fields(self):
        return [(Various.signed.base, const.SignedWORD),
                (Various.unsigned.base, const.WORD),
                (Various.chars.base, const.Char)]

    def test_lengths(self):
        self.assertEqual(len(Various.signed), 3 * 2)
        self.assertEqual(len(Various.unsigned), 4 * 2)
        self.assertEqual(len(Various.bools), 6 * 1)
        self.assertEqual(len(Various.chars), 8 * 1)
        self.assertEqual(len(Various), 3 * 2 + 4 * 2 + 6 * 1 + 8 * 1)
        self.assertEqual(len(self.obj), 3 * 2 + 4 * 2 + 6 * 1 + 8 * 1)
        self.assertEqual(len(self.obj.signed), 3)
        self.assertEqual(len(self.obj.unsigned), 4)
        self.assertEqual(len(self.obj.bools), 6)
        self.assertEqual(len(self.obj.chars), 8)

    def test_invalid_value_assignments(self):
        with self.assertRaises(ValueError):
            self.obj.chars = ''
        with self.assertRaises(ValueError):
            self.obj.chars = 'abcdefg'
        with self.assertRaises(ValueError):
            self.obj.bools = (True,) * 5 + ('',)

    def test_char_array_as_string(self):
        self.obj.chars = 'abcdefgh'
        self.assertEqual(self.obj.pack(), self.buff)

    def test_count(self):
        self.assertEqual(Various.signed.count, 3)
        self.assertEqual(Various.unsigned.count, 4)
        self.assertEqual(Various.bools.count, 6)
        self.assertEqual(Various.chars.count, 8)


if __name__ == '__main__':
    unittest.main()
