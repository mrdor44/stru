from stru.enhanced_struct import Endianess
from stru.field_type import FieldType
from stru.stru_struct import Struct
from stru_tests.struct_test_case import StructTestCase, const

import unittest


class LittleEndianPoint(Struct):
    _endianess = Endianess.LittleEndian
    x = FieldType.WORD
    y = FieldType.WORD


class BigEndianPoint(Struct):
    _endianess = Endianess.BigEndian
    x = FieldType.WORD
    y = FieldType.WORD


class NetworkPoint(Struct):
    _endianess = Endianess.Network
    x = FieldType.WORD
    y = FieldType.WORD


class NativePoint(Struct):
    _endianess = Endianess.Network
    x = FieldType.WORD
    y = FieldType.WORD


class StandardNativePoint(Struct):
    _endianess = Endianess.StandardNative
    x = FieldType.WORD
    y = FieldType.WORD


# noinspection PyUnresolvedReferences
class AbstractPointTests(StructTestCase):
    def get_target_class(self):
        raise NotImplementedError()

    def get_buffer(self):
        raise NotImplementedError()

    def create_target(self):
        return self.get_target_class()(x=1, y=2), self.get_buffer()

    def get_fields(self):
        return [(self.cls.x, const.WORD),
                (self.cls.y, const.WORD)]

    def test_lengths(self):
        for field, _ in self.get_fields():
            self.assertEqual(len(field), 2)
        self.assertEqual(len(self.cls), 4)
        self.assertEqual(len(self.obj), 4)

    def test_invalid_value_assignment(self):
        with self.assertRaises(ValueError):
            self.obj.x = self.cls.x.upper_limit
        with self.assertRaises(ValueError):
            self.obj.y = self.cls.y.upper_limit
        with self.assertRaises(ValueError):
            self.obj.x = self.cls.x.lower_limit
        with self.assertRaises(ValueError):
            self.obj.y = self.cls.y.lower_limit


# noinspection PyPep8Naming
class BasicTests_LittleEndianPoint(AbstractPointTests, unittest.TestCase):
    def get_target_class(self):
        return LittleEndianPoint

    def get_buffer(self):
        return b'\x01\x00\x02\x00'


# noinspection PyPep8Naming,PyTypeChecker
class BasicTests_BigEndianPoint(AbstractPointTests, unittest.TestCase):
    def get_target_class(self):
        return BigEndianPoint

    def get_buffer(self):
        return b'\x00\x01\x00\x02'


# noinspection PyPep8Naming,PyTypeChecker
class BasicTests_NetworkPoint(AbstractPointTests, unittest.TestCase):
    def get_target_class(self):
        return NetworkPoint

    def get_buffer(self):
        return b'\x00\x01\x00\x02'


# noinspection PyPep8Naming,PyTypeChecker
class BasicTests_NativePoint(AbstractPointTests, unittest.TestCase):
    def get_target_class(self):
        return NativePoint

    def get_buffer(self):
        return b'\x00\x01\x00\x02'


# noinspection PyPep8Naming,PyTypeChecker
class BasicTests_StandardNativePoint(AbstractPointTests, unittest.TestCase):
    def get_target_class(self):
        return StandardNativePoint

    def get_buffer(self):
        return b'\x01\x00\x02\x00'


if __name__ == '__main__':
    unittest.main()
