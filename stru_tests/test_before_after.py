from stru import Endianess, FieldType
from stru.stru_struct import Struct
from stru_tests.struct_test_case import StructTestCase, const

import unittest


def asserter(expected):
    def _asserter(value):
        assert value == expected

    return _asserter


class Altered(Struct):
    _endianess = Endianess.BigEndian
    x = FieldType.WORD(default=10,
                       before_pack=asserter(10), before_unpack=asserter('\x00\x0a'),
                       after_pack=asserter('\x00\x0a'), after_unpack=asserter(10))
    y = FieldType.BYTE[2](default=[11, 12],
                          before_pack=asserter([11, 12]), before_unpack=asserter('\x0b\x0c'),
                          after_pack=asserter('\x0b\x0c'), after_unpack=asserter([11, 12]))


class BeforeAfterTests(StructTestCase, unittest.TestCase):
    def create_target(self):
        obj = Altered()
        buff = '\x00\x0a' '\x0b\x0c'
        return obj, buff

    def get_fields(self):
        return [(Altered.x, const.WORD),
                (Altered.y.base, const.BYTE)]


if __name__ == '__main__':
    unittest.main()
