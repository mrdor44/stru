# TODO: Replace with BytesIO
from io import StringIO, BytesIO


class UnpackStream(object):
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    def read(self, amount):
        raise NotImplementedError()

    @classmethod
    def create(cls, stream_obj, *args, **kwargs):
        if isinstance(stream_obj, cls):
            return stream_obj
        elif callable(stream_obj):
            return CallableStream(stream_obj, *args, **kwargs)
        elif isinstance(stream_obj, str):
            return StringBufferStream(stream_obj, *args, **kwargs)
        elif isinstance(stream_obj, bytes):
            return BytesBufferStream(stream_obj, *args, **kwargs)
        else:
            raise TypeError("Can't use object of type {} as input stream".format(type(stream_obj).__name__))


class StringBufferStream(UnpackStream):
    def __init__(self, buff, *args, **kwargs):
        super(StringBufferStream, self).__init__(*args, **kwargs)
        self._buff = StringIO(buff)
        self._length = len(buff)

    def read(self, amount):
        return self._buff.read(amount)

    def __len__(self):
        return self._length - self._buff.tell()


# TODO: Reach 100% Coverage
# TODO: Use Struct
# TODO: Unite this with StringBufferStream
class BytesBufferStream(UnpackStream):
    def __init__(self, buff, *args, **kwargs):
        super(BytesBufferStream, self).__init__(*args, **kwargs)
        self._buff = BytesIO(buff)
        # TODO: Is this needed?
        self._length = len(buff)

    def read(self, amount):
        return self._buff.read(amount)

    def __len__(self):
        return self._length - self._buff.tell()


class CallableStream(UnpackStream):
    def __init__(self, get_next, *args, **kwargs):
        super(CallableStream, self).__init__(*args, **kwargs)
        self._get_next = get_next

    def read(self, amount):
        data = self._get_next(amount, *self._args, **self._kwargs)
        return data
