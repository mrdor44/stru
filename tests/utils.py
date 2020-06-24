from io import BytesIO


# noinspection PyPep8Naming
class const(object):
    class Char(object):
        MAX = chr(255)
        MIN = chr(0)

    class BYTE(object):
        MAX = (2 ** 8) - 1
        MIN = 0
        UPPER_LIMIT = 2 ** 8
        LOWER_LIMIT = -1

    class SignedBYTE(object):
        MAX = (2 ** 7) - 1
        MIN = -(2 ** 7)
        UPPER_LIMIT = 2 ** 7
        LOWER_LIMIT = -(2 ** 7) - 1

    class WORD(object):
        MAX = (2 ** 16) - 1
        MIN = 0
        UPPER_LIMIT = 2 ** 16
        LOWER_LIMIT = -1

    class SignedWORD(object):
        MAX = (2 ** 15) - 1
        MIN = -(2 ** 15)
        UPPER_LIMIT = 2 ** 15
        LOWER_LIMIT = -(2 ** 15) - 1

    class DWORD(object):
        MAX = (2 ** 32) - 1
        MIN = 0
        UPPER_LIMIT = 2 ** 32
        LOWER_LIMIT = -1

    class SignedDWORD(object):
        MAX = (2 ** 31) - 1
        MIN = -(2 ** 31)
        UPPER_LIMIT = 2 ** 31
        LOWER_LIMIT = -(2 ** 31) - 1

    class QWORD(object):
        MAX = (2 ** 64) - 1
        MIN = 0
        UPPER_LIMIT = 2 ** 64
        LOWER_LIMIT = -1

    class SignedQWORD(object):
        MAX = (2 ** 63) - 1
        MIN = -(2 ** 63)
        UPPER_LIMIT = 2 ** 63
        LOWER_LIMIT = -(2 ** 63) - 1


# noinspection PyPep8Naming,PyUnresolvedReferences
class EnhancedStructTestCase(object):
    def __init__(self, *args, **kwargs):
        # noinspection PyArgumentList
        super(EnhancedStructTestCase, self).__init__(*args, **kwargs)
        self.obj = None
        self.buff = None
        self.cls = None

    def setUp(self):
        self.obj, self.buff = self.create_target()
        self.cls = type(self.obj)

    def create_target(self):
        raise NotImplementedError()

    def get_fields(self):
        return []

    def test_pack(self):
        self.assertEqual(self.buff, self.obj.pack())

    def test_unpack(self):
        self.assertEqual(self.cls.unpack(self.buff), self.obj)

    def test_unpack_stream(self):
        self.assertEqual(self.cls.unpack(BytesIO(self.buff).read), self.obj)

    def test_pack_unpack(self):
        self.assertEqual(self.cls.unpack(self.buff).pack(), self.buff)
        self.assertEqual(self.cls.unpack(self.obj.pack()), self.obj)

    def test_pack_unpack_stream(self):
        self.assertEqual(self.cls.unpack(BytesIO(self.buff).read).pack(), self.buff)
        self.assertEqual(self.cls.unpack(BytesIO(self.obj.pack()).read), self.obj)

    def test_max_min_limits(self):
        for field, _const in self.get_fields():
            self.assertEqual(field.max, _const.MAX)
            self.assertEqual(field.min, _const.MIN)
            if hasattr(field, 'upper_limit'):
                self.assertEqual(field.upper_limit, _const.UPPER_LIMIT)
                self.assertEqual(field.lower_limit, _const.LOWER_LIMIT)

    def _assert_unpacked(self, unpacked_obj):
        self.assertEquals(self.obj, unpacked_obj)
