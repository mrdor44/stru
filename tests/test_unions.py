from stru import (Struct, Endianess, FieldType, UnsupportedOperationException,
                  DependencyInvalidValueException, DependencyNoneException, DependencyNotInClassException)
from tests.utils import EnhancedStructTestCase, const

import unittest


class MyWord(Struct):
    _endianess = Endianess.LittleEndian
    a = FieldType.WORD


class Onion(Struct):
    _endianess = Endianess.BigEndian
    a = FieldType.SignedBYTE
    b = FieldType.Union(a, {
        -10: FieldType.String[4],
        -3: FieldType.Bool,
        1: FieldType.UnsignedInt,
        2: FieldType.Int,
    })
    c = FieldType.BYTE
    d = FieldType.Union(b, {
        'ab': FieldType.Short[3],
        'c': FieldType.Char(default='z'),
        400: FieldType.Union(c, {
            1: FieldType.Struct(MyWord)
        })
    })


class UnionTests1(EnhancedStructTestCase, unittest.TestCase):
    def create_target(self):
        obj = Onion(a=-10, b='ab', c=0xFF, d=[1, 2, 3])
        buff = '\xf6' 'ab\x00\x00' '\xff' '\x00\x01\x00\x02\x00\x03'
        return obj, buff

    def get_fields(self):
        return [(Onion.b[1], const.DWORD),
                (Onion.b[2], const.SignedDWORD),
                (Onion.d['ab'].base, const.SignedWORD),
                (Onion.d['c'], const.Char),
                (Onion.d[400][1].base.a, const.WORD)]

    def test_lengths(self):
        with self.assertRaises(UnsupportedOperationException):
            len(Onion.b)
        with self.assertRaises(UnsupportedOperationException):
            len(Onion.d)
        with self.assertRaises(UnsupportedOperationException):
            len(Onion)
        self.assertEqual(len(self.obj), len(self.buff))

    def test_invalid_value_assignments(self):
        with self.assertRaises(TypeError):
            self.obj.b = 4
        with self.assertRaises(TypeError):
            self.obj.d = 4
        with self.assertRaises(ValueError):
            self.obj.b = 'sadfsadfsadf'


class UnionTests2(EnhancedStructTestCase, unittest.TestCase):
    def create_target(self):
        obj = Onion(a=-10, b='c', c=0xFF, d='a')
        buff = '\xf6' 'c\x00\x00\x00' '\xff' 'a'
        return obj, buff

    def test_lengths(self):
        self.assertEqual(len(self.obj), len(self.buff))


class UnionTests3(EnhancedStructTestCase, unittest.TestCase):
    def create_target(self):
        obj = Onion(a=1, b=400, c=1, d=MyWord(a=2))
        buff = '\x01' '\x00\x00\x01\x90' '\x01' '\x02\x00'
        return obj, buff

    def test_lengths(self):
        self.assertEqual(len(self.obj), len(self.buff))


class UnionDefaultsTests(unittest.TestCase):
    def test_default_does_nothing(self):
        obj = Onion(a=-10, b='c', c=0)
        self.assertIsNone(obj.d)


class UnionExceptionTests(unittest.TestCase):
    def test_invalid_selector(self):
        with self.assertRaises(DependencyInvalidValueException):
            Onion(a=0, b=0, c=0, d=0)

    def test_missing_selector(self):
        with self.assertRaises(DependencyNoneException):
            Onion(b=400, c=1, d=MyWord(a=2))

    def test_selector_not_in_class(self):
        x = 5

        class JustWrong(Struct):
            _endianess = Endianess.BigEndian
            data = FieldType.Union(x, {
                1: FieldType.DWORD
            })

        with self.assertRaises(DependencyNotInClassException):
            JustWrong(data=2)


if __name__ == '__main__':
    unittest.main()
