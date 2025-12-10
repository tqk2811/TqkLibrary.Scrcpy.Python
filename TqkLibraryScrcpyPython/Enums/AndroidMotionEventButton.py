# Tên file gốc: AndroidMotionEventButton.cs
from enum import IntFlag

class AndroidMotionEventButton(IntFlag):
    """
    TqkLibrary.Scrcpy.Enums.AndroidMotionEventButton
    https://developer.android.com/reference/android/view/MotionEvent#BUTTON_PRIMARY
    Kiểu cơ sở: int
    """
    BUTTON_NONE = 0
    BUTTON_PRIMARY = 1
    BUTTON_SECONDARY = 2
    BUTTON_TERTIARY = 4
    BUTTON_BACK = 8
    BUTTON_FORWARD = 16
    BUTTON_STYLUS_PRIMARY = 32
    BUTTON_STYLUS_SECONDARY = 64