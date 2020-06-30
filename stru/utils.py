# Windows 1252 is the 8 bit character encoding of the latin alphabet, extending ASCII
# https://en.wikipedia.org/wiki/Windows-1252
ENCODING = 'cp1252'


def int2byte(i: int) -> bytes:
    """
    Convert an int to bytes using 8 bit encoding
    :param i: The int to convert
    :return: The bytes representation
    """
    return str2bytes(chr(i))


def byte2int(b: bytes) -> int:
    """
    Convert bytes to an int using 8 bit encoding
    :param b: The bytes to convert
    :return: The integer representation
    """
    return ord(b)


def str2bytes(s: str) -> bytes:
    """
    Convert an str to bytes using 8 bit encoding
    :param s: The str to convert
    :return: The bytes representation
    """
    return s.encode(ENCODING)


def bytes2str(b: bytes) -> str:
    """
    Convert bytes to an str using 8 bit encoding
    :param b: The bytes to convert
    :return: The str representation
    """
    return b.decode(ENCODING)
