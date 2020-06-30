from stru import Struct, Endianess, FieldType
from stru_tests.struct_test_case import StructTestCase

import unittest


class Person(Struct):
    _endianess = Endianess.BigEndian
    initial = FieldType.String
    name = FieldType.String[10]
    age = FieldType.BYTE


class StringsTest(StructTestCase, unittest.TestCase):
    def create_target(self):
        obj = Person(initial='r', name='Wayne', age=25)
        buff = b'rWayne\x00\x00\x00\x00\x00\x19'
        return obj, buff

    def test_lengths(self):
        self.assertEqual(len(Person.initial), 1)
        self.assertEqual(len(Person.name), 10)
        self.assertEqual(len(Person.age), 1)
        self.assertEqual(len(Person), 12)
        self.assertEqual(len(self.obj), 12)
        self.assertEqual(len(self.obj.initial), 1)
        self.assertEqual(len(self.obj.name), 5)

    def test_assignments(self):
        with self.assertRaises(TypeError):
            self.obj.initial = 14
        with self.assertRaises(ValueError):
            self.obj.initial = 'aa'
        with self.assertRaises(TypeError):
            self.obj.name = 14
        with self.assertRaises(ValueError):
            self.obj.name = 'a' * 11

        self.obj.initial = ''
        self.obj.name = ''


if __name__ == '__main__':
    unittest.main()
