# Tên file gốc: ScrcpyControlType.cs
from enum import Enum

class ScrcpyControlType(Enum):
    """
    TqkLibrary.Scrcpy.Enums.ScrcpyControlType
    https://github.com/Genymobile/scrcpy/tree/master/server/src/main/java/com/genymobile/scrcpy/ControlMessage.java#L8
    Kiểu cơ sở: byte

    CẢNH BÁO: số hiệu đã đổi ở scrcpy 4.0 so với 2.4 — TYPE_UHID_DESTROY chèn vào 14 và đẩy
    OPEN_HARD_KEYBOARD_SETTINGS sang 15. Server KHÔNG validate: gửi số cũ thì nó thực thi nhầm
    lệnh khác chứ không báo lỗi.
    """
    TYPE_INJECT_KEYCODE = 0
    TYPE_INJECT_TEXT = 1
    TYPE_INJECT_TOUCH_EVENT = 2
    TYPE_INJECT_SCROLL_EVENT = 3
    TYPE_BACK_OR_SCREEN_ON = 4
    TYPE_EXPAND_NOTIFICATION_PANEL = 5
    TYPE_EXPAND_SETTINGS_PANEL = 6
    TYPE_COLLAPSE_PANELS = 7
    TYPE_GET_CLIPBOARD = 8
    TYPE_SET_CLIPBOARD = 9
    TYPE_SET_DISPLAY_POWER = 10
    TYPE_ROTATE_DEVICE = 11
    TYPE_UHID_CREATE = 12
    TYPE_UHID_INPUT = 13
    TYPE_UHID_DESTROY = 14
    OPEN_HARD_KEYBOARD_SETTINGS = 15
    TYPE_START_APP = 16
    TYPE_RESET_VIDEO = 17
    TYPE_CAMERA_SET_TORCH = 18
    TYPE_CAMERA_ZOOM_IN = 19
    TYPE_CAMERA_ZOOM_OUT = 20
    TYPE_RESIZE_DISPLAY = 21