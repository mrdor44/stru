class Endianess(object):
    Native = '@'  # Native format, native size
    StandardNative = '='  # Native format, standard size
    LittleEndian = '<'  # Standard size
    BigEndian = '>'  # Standard size
    Network = '!'  # Network order


class MissingEndianessException(Exception):
    pass


