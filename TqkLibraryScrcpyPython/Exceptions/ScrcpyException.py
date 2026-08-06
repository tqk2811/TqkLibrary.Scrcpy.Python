# TqkLibrary.Scrcpy.Python/Exceptions/ScrcpyException.py
# Mirror ScrcpyException.cs


class ScrcpyException(Exception):
    """Lỗi phát sinh khi thao tác với scrcpy (adb, server, protocol)."""
    pass


class InvalidRangeException(ScrcpyException):
    """Giá trị nằm ngoài khoảng scrcpy protocol cho phép."""
    pass
