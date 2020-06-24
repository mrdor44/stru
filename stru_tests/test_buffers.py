from stru import (Endianess, FieldType, UnsupportedOperationException,
                  DependencyNoneException, DependencyInvalidValueException, DependencyNotInClassException)
from stru.stru_struct import Struct
from stru_tests.struct_test_case import StructTestCase

import unittest


class Boo(Struct):
    _endianess = Endianess.Network
    a = FieldType.SignedBYTE
    b = FieldType.BYTE
    c = FieldType.Buffer(a)


class BuffersTests(StructTestCase, unittest.TestCase):
    def create_target(self):
        obj = Boo(a=4, b=2, c='abcd')
        buff = '\x04\x02abcd'
        return obj, buff

    def test_lengths(self):
        with self.assertRaises(UnsupportedOperationException):
            len(Boo.c)
        with self.assertRaises(UnsupportedOperationException):
            len(Boo)
        self.assertEqual(len(self.obj), len(self.buff))

    def test_invalid_value_assignmentS(self):
        with self.assertRaises(TypeError):
            self.obj.c = [4, 4, 4, 4]
        with self.assertRaises(ValueError):
            self.obj.c = 'abcde'
        self.obj.a = 2
        with self.assertRaises(ValueError):
            self.obj.c = 'abcd'
        self.obj.c = 'ab'


class BuffersWithNullTerminatorsTests(StructTestCase, unittest.TestCase):
    def create_target(self):
        obj = Boo(a=4, b=2, c='\x00a\x00b')
        buff = '\x04\x02\x00a\x00b'
        return obj, buff


class BufferExceptionsTests(unittest.TestCase):
    def test_invalid_length(self):
        with self.assertRaises(DependencyInvalidValueException):
            Boo(a=-1, c='a')

    def test_missing_length(self):
        with self.assertRaises(DependencyNoneException):
            Boo(c='a')

    def test_length_not_in_class(self):
        x = 5

        class JustWrong(Struct):
            _endianess = Endianess.BigEndian
            data = FieldType.Buffer(x)

        with self.assertRaises(DependencyNotInClassException):
            JustWrong(data=2)


if __name__ == '__main__':
    unittest.main()
