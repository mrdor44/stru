# stru
**Stru** is a **flexible** and **declarative** binary structured data library, much like Python's `struct` module. With Stru, you **declare your structs C-style**, while maintaining all of Python's upside.

The key difference between Stru and Python's `struct` is that Python's `struct` is imperative, meaning the coder tells `struct` how to parse the data, while Stru is **declarative**, meaning the coder tells Stru *how the data looks like*.

Stru provides anything from simple `struct`-like constructs that can be used as one-on-one alternatives, to more complex constructs that further extend the `struct` module features.

For example, consider the following C-style struct:

```c++
struct message {
    uint32_t length;
    uint8_t magic;
    uint8_t* buffer; // buffer length indicated by length field
};
```

Packing this struct into binary form using Python's `struct` would look like the following code:

```python
import struct
buffer = b'ABCD'
message = struct.pack(f'LB{len(buffer)}s', len(buffer), 0xEF, buffer)
```

On the other hand, packing this struct using Stru would look like the following code:

```python
from stru import Struct, FieldType
class Message(Struct):
    length = FieldType.UnsignedInt
    magic = FieldType.BYTE(default=0xEF)
    buffer = FieldType.Buffer(length)
buffer=b'ABCD'
message = Message(length=len(buffer), buffer=buffer).pack()
```

So who needs to mess around with unreadable format strings and ambiguous letters? Start using Stru to enjoy the full power of `struct` and even more.