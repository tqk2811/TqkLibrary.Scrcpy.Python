import abc
import typing
from typing import Optional, Any
import numpy as np # Dành cho GetScreenShot
from ..Events import (
    DisconnectEvent,
    ClipboardEvent,
)
from ..Configs import(
    ScrcpyConfig
)
from ..Structs import(
    Size,
)
from ..NativeWrapper import (
    RegisterClipboardEvent, NativeOnClipboardReceivedDelegate,
    RegisterClipboardAcknowledgementEvent, NativeOnClipboardAcknowledgementDelegate,
)
if typing.TYPE_CHECKING:
    from .Interfaces import IControl
else:
    IControl = Any

# --- Giao diện IScrcpy ---

class IScrcpy(abc.ABC):
    """
    Giao diện mô phỏng cho Scrcpy Core.
    Bao gồm các thuộc tính, phương thức công khai, và các phương thức giao tiếp
    cần thiết cho ScrcpyControl.
    """
    
    # --- Thuộc tính (Properties) ---

    @property
    @abc.abstractmethod
    def DeviceId(self) -> str:
        """ID của thiết bị."""
        pass
    
    @property
    @abc.abstractmethod
    def DeviceName(self) -> str:
        """Tên thiết bị."""
        pass

    @property
    @abc.abstractmethod
    def IsConnected(self) -> bool:
        """Trạng thái kết nối."""
        pass

    @property
    @abc.abstractmethod
    def ScreenSize(self) -> Size:
        """Kích thước màn hình (Width, Height)."""
        pass
        
    @property
    @abc.abstractmethod
    def LastClipboard(self) -> str:
        """Giá trị clipboard cuối cùng được nhận."""
        pass
    
    @property
    @abc.abstractmethod
    def Control(self) -> IControl:
        """Đối tượng điều khiển (Control object) đã được khởi tạo."""
        # Dùng IControl (interface) thay vì ScrcpyControl (concrete class)
        pass

    # --- Sự kiện/Callback (Events/Callbacks) ---

    @property
    @abc.abstractmethod
    def OnDisconnect(self) -> DisconnectEvent:
        """Sự kiện/Callback khi kết nối bị ngắt."""
        pass

    @property
    def OnClipboardReceived(self) -> ClipboardEvent:
        """Sự kiện clipboard"""
        pass

    # --- Phương thức Chính (Public Methods) ---

    @abc.abstractmethod
    def Connect(self, config: Optional[ScrcpyConfig] = None) -> bool:
        """Thiết lập kết nối với thiết bị."""
        pass

    @abc.abstractmethod
    def Stop(self) -> None:
        """Dừng kết nối Scrcpy."""
        pass

    @abc.abstractmethod
    def GetScreenShot(self) -> Optional[np.ndarray]:
        """Chụp ảnh màn hình và trả về dưới dạng numpy array."""
        pass

    @abc.abstractmethod
    def Dispose(self, disposing: bool = True) -> None:
        """Giải phóng tài nguyên."""
        pass
        
    # --- Phương thức Giao tiếp Bắt buộc cho IControl ---
    # Các phương thức này được gọi bởi ScrcpyControl trong ctor và phương thức SendControl.

    @abc.abstractmethod
    def SendControl(self, command: bytes) -> bool:
        """Gửi lệnh điều khiển nhị phân đến thiết bị."""
        pass

    @abc.abstractmethod
    def _register_clipboard_event(self, method: NativeOnClipboardReceivedDelegate) -> bool:
        pass

    @abc.abstractmethod
    def _register_clipboard_acknowledgement_event(self, method: NativeOnClipboardReceivedDelegate) -> bool:
        pass

    @abc.abstractmethod
    def _set_last_clipboard(self, data: str) -> None:
        pass