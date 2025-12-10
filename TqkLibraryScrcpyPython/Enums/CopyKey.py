# Tên file gốc: CopyKey.cs
from enum import Enum

class CopyKey(Enum):
    """
    TqkLibrary.Scrcpy.Enums.CopyKey
    """
    None_ = 0  # Đổi tên thành None_ để tránh xung đột với từ khóa 'None' của Python
    Copy = 1
    Cut = 2