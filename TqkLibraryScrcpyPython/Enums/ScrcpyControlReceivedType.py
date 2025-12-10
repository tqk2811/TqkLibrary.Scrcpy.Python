# Tên file gốc: ScrcpyControlReceivedType.cs
from enum import Enum

class ScrcpyControlReceivedType(Enum):
    """
    TqkLibrary.Scrcpy.Enums.ScrcpyControlReceivedType
    https://github.com/Genymobile/scrcpy/blob/master/app/src/receiver.c#L25
    Kiểu cơ sở: byte
    """
    DEVICE_MSG_TYPE_CLIPBOARD = 0