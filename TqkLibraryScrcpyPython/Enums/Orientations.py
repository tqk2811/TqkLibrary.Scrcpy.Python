# Tên file gốc: Orientations.cs
from enum import IntEnum

class Orientations(IntEnum):
    """TqkLibrary.Scrcpy.Enums.Orientations. Kiểu cơ sở: int"""
    Auto = -1
    Natural = 0
    Counterclockwise90 = 1
    Flip = 2  # 180°
    Clockwise90 = 3