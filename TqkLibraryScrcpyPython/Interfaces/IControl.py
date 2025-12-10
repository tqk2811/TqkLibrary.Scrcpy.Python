import abc
import typing
from typing import Any, List, Dict, Callable, Optional
from collections import namedtuple

from ..Structs import *
from ..Enums import *
from ..Controls.ScrcpyMousePointerId import(
    ScrcpyMousePointerId
)
from .IScrcpy import IScrcpy

if typing.TYPE_CHECKING:
    from .interfaces import IControl
else:
    IControl = Any

# --- Định nghĩa Delegate (Kiểu dữ liệu) ---
# Tương đương với public delegate void OnDataReceived<T>(IControl control, T data);
# Kiểu Generic này được triển khai bằng typing.Callable
OnDataReceived = typing.Callable[[IControl, Any], None]

# --- Giao diện IControl ---

class IControl(abc.ABC):
    """
    Giao diện mô phỏng cho Scrcpy Control.
    Tương đương với giao diện IControl.cs trong C#.
    """
    
    # --- Thuộc tính ---
    
    @property
    @abc.abstractmethod
    def Scrcpy(self) -> IScrcpy:
        """Trả về instance Scrcpy cốt lõi."""
        pass


    # --- Phương thức điều khiển (Control Methods) ---

    @abc.abstractmethod
    def InjectKeycode(
        self,
        action: AndroidKeyEventAction,
        keycode: AndroidKeyCode,
        repeat: int,
        meta_state: AndroidKeyEventMeta
    ) -> bool:
        """Gửi lệnh inject keycode."""
        pass

    @abc.abstractmethod
    def InjectText(self, text: str) -> bool:
        """Gửi lệnh inject text. Chỉ hỗ trợ ASCII/No unicode (theo tài liệu gốc)."""
        pass

    @abc.abstractmethod
    def InjectTouchEvent(
        self,
        action: AndroidMotionEventAction,
        pointer_id: int,
        position: Rectangle,
        pressure: float,
        buttons: AndroidMotionEventButton,
        action_button: AndroidMotionEventButton
    ) -> bool:
        """
        Gửi lệnh inject touch event.
        * `pointer_id`: Sử dụng `ScrcpyMousePointerId.POINTER_ID_MOUSE` hoặc `ScrcpyMousePointerId.POINTER_ID_VIRTUAL_MOUSE` cho chuột; nếu không, sử dụng ngón tay.
        * `pressure`: Khi `AndroidMotionEventAction.ACTION_DOWN` hoặc `AndroidMotionEventAction.ACTION_MOVE` là 1.0f, ngược lại là 0.0f.
        * `buttons`: Thay đổi nút.
        * `action_button`: Trạng thái hiện tại của tất cả các nút.
        """
        pass

    @abc.abstractmethod
    def InjectScrollEvent(
        self,
        position: Rectangle,
        v_scroll: float,
        h_scroll: float,
        button: AndroidMotionEventButton
    ) -> bool:
        """Gửi lệnh inject scroll event."""
        pass

    @abc.abstractmethod
    def SetClipboard(self, text: str, paste: bool, sequence: Optional[int] = None) -> bool:
        """Thiết lập clipboard mà không có sequence."""
        pass
    
    @abc.abstractmethod
    def GetClipboard(self, copy_key: CopyKey) -> bool:
        """
        Lấy dữ liệu clipboard. 
        Kích hoạt sự kiện `on_clipboard_received`.
        """
        pass

    @abc.abstractmethod
    def SetScreenPowerMode(self, power_mode: ScrcpyScreenPowerMode) -> bool:
        """Thiết lập chế độ nguồn màn hình."""
        pass

    @abc.abstractmethod
    def BackOrScreenOn(self, key_event_action: AndroidKeyEventAction) -> bool:
        """Thực hiện hành động cho nút Back trong android."""
        pass

    @abc.abstractmethod
    def ExpandNotificationPanel(self) -> bool:
        """Mở rộng bảng thông báo."""
        pass

    @abc.abstractmethod
    def ExpandSettingsPanel(self) -> bool:
        """Mở rộng bảng cài đặt."""
        pass

    @abc.abstractmethod
    def CollapsePanel(self) -> bool:
        """Thu gọn bảng thông báo/cài đặt."""
        pass

    @abc.abstractmethod
    def RotateDevice(self) -> bool:
        """Xoay thiết bị."""
        pass

    @abc.abstractmethod
    def OpenHardKeyboardSetting(self) -> bool:
        """Mở cài đặt bàn phím cứng."""
        pass