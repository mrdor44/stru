from stru import Struct, FieldType, Endianess

import unittest


class BasePoint(Struct):
    x = FieldType.WORD
    y = FieldType.WORD


class Point1(BasePoint):
    _endianess = Endianess.BigEndian


class Point2(BasePoint):
    _endianess = Endianess.BigEndian


class Point3(BasePoint):
    _endianess = Endianess.LittleEndian


class Point4(BasePoint):
    _endianess = Endianess.BigEndian
    z = FieldType.WORD


class EqualityTests(unittest.TestCase):
    def setUp(self):
        self.p11 = Point1(x=1, y=2)
        self.p12 = Point1(x=1, y=3)
        self.p2 = Point2(x=1, y=2)
        self.p3 = Point3(x=1, y=2)
        self.p4 = Point4(x=1, y=2)

    def test_same_object(self):
        self.assertTrue(self.p11 == self.p11)
        self.assertTrue(self.p12 == self.p12)
        self.assertTrue(self.p2 == self.p2)
        self.assertTrue(self.p3 == self.p3)
        self.assertTrue(self.p4 == self.p4)
        self.assertFalse(self.p11 != self.p11)
        self.assertFalse(self.p12 != self.p12)
        self.assertFalse(self.p2 != self.p2)
        self.assertFalse(self.p3 != self.p3)
        self.assertFalse(self.p4 != self.p4)

    def test_same_class_not_equal(self):
        self.assertTrue(self.p11 != self.p12)
        self.assertFalse(self.p11 == self.p12)

    def test_different_class_same_attributes(self):
        self.assertTrue(self.p11 != self.p2)
        self.assertFalse(self.p11 == self.p2)
        self.assertTrue(self.p11 != self.p4)
        self.assertFalse(self.p11 == self.p4)

    def test_different_class_different_attributes(self):
        self.assertTrue(self.p11 != self.p3)
        self.assertFalse(self.p11 == self.p3)


if __name__ == '__main__':
    unittest.main()
