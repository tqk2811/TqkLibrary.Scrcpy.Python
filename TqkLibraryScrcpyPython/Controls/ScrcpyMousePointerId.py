import typing

class ScrcpyMousePointerId:
    """
    Tương đương với ScrcpyMousePointerId.cs
    Các hằng số cho ID con trỏ chuột/chạm trong scrcpy.
    """
    POINTER_ID_MOUSE: typing.ClassVar[int] = -1
    """Mouse pointer ID: -1"""

    POINTER_ID_GENERIC_FINGER: typing.ClassVar[int] = -2
    """Generic finger pointer ID: -2"""

    POINTER_ID_VIRTUAL_MOUSE: typing.ClassVar[int] = -3
    """Virtual mouse pointer ID: -3"""

    POINTER_ID_VIRTUAL_FINGER: typing.ClassVar[int] = -4
    """Virtual finger pointer ID: -4"""

# Ví dụ sử dụng:
# print(ScrcpyMousePointerId.POINTER_ID_MOUSE)