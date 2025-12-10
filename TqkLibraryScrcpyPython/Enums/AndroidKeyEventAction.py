# Tên file gốc: AndroidKeyEventAction.cs
from enum import Enum

class AndroidKeyEventAction(Enum):
    """
    TqkLibrary.Scrcpy.Enums.AndroidKeyEventAction
    https://developer.android.com/reference/android/view/KeyEvent#ACTION_DOWN
    Kiểu cơ sở: byte
    """
    ACTION_DOWN = 0
    ACTION_UP = 1
    ACTION_MULTIPLE = 2  # API level < 29