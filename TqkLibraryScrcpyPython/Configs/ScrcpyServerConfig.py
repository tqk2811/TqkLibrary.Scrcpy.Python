# TqkLibrary.Scrcpy.Python/Configs/ScrcpyServerConfig.py

from typing import Optional, Iterable
from .BaseConfig import BaseConfig
from .AndroidConfig import AndroidConfig
from .AudioConfig import AudioConfig
from .VideoConfig import VideoConfig
from .CameraConfig import CameraConfig
from ..Enums.VideoSource import VideoSource
from ..Enums.LogLevel import LogLevel
from ..Enums.DisplayImePolicy import DisplayImePolicy
from .. import Constant


class ScrcpyServerConfig(BaseConfig):

    def __init__(self):
        # Config Sub-classes
        self.AndroidConfig: Optional[AndroidConfig] = AndroidConfig()
        self.VideoConfig: Optional[VideoConfig] = VideoConfig()
        self.AudioConfig: Optional[AudioConfig] = AudioConfig()
        self.CameraConfig: Optional[CameraConfig] = CameraConfig()

        # Properties
        self.IsVideo: bool = True
        self.VideoSource: VideoSource = VideoSource.Display
        self.IsControl: bool = True
        self.LogLevel: LogLevel = LogLevel.Info
        self.SCID: int = -1
        self.ClipboardAutosync: bool = False
        self.Cleanup: bool = False
        self.TunnelForward: bool = False  # do not change
        self.MaxSize: int = 0

        # Tắt màn hình sau khoảng trễ này (ms). -1 = không giới hạn (mặc định). scrcpy 3.0
        self.ScreenOffTimeout: int = -1

        # Tạo display ảo với độ phân giải + dpi chỉ định.
        # Dạng: "[<width>x<height>][/<dpi>]" vd "1920x1080/320", hoặc "" để dùng mặc định thiết bị.
        # None = bỏ qua (dùng màn hình vật lý). scrcpy 3.0
        self.NewDisplay: Optional[str] = None

        # Hiện system decoration trên display ảo. False -> phát vd_system_decorations=false. scrcpy 3.0
        self.VdSystemDecorations: bool = True

        # Huỷ nội dung (đưa task về display chính) khi display ảo đóng.
        # False -> phát vd_destroy_content=false. scrcpy 3.1
        self.VdDestroyContent: bool = True

        # Chính sách IME trên display đang capture. None = bỏ qua (mặc định server). scrcpy 3.2
        self.DisplayImePolicy: Optional[DisplayImePolicy] = None

        # Giữ thiết bị "active" (không để display bị idle/dim) khi scrcpy đang chạy. scrcpy 4.0
        self.KeepActive: bool = False

        # Version string gửi cho server, phải khớp scrcpy-server.jar đang deploy.
        self.ScrcpyServerVersion: str = Constant.ScrcpyServerVersion  # do not change

    def _get_server_arguments(self) -> Iterable[str]:
        """Tham số dành cho Server Config. Chỉ phát ra khi value khác mặc định của scrcpy-server."""
        yield self.ScrcpyServerVersion
        # video=false chỉ phát khi IsVideo=False (server default true)
        yield self._get_argument("video", self.IsVideo, condition=lambda x: not x)
        # control=false chỉ phát khi IsControl=False
        yield self._get_argument("control", self.IsControl, condition=lambda x: not x)
        yield self._get_argument(
            "scid", self.SCID,
            condition=lambda x: x != -1,
            formatter=lambda x: f"{(x & 0x7FFFFFFF):04x}",
        )
        # clipboard_autosync=false chỉ phát khi False (server default true)
        yield self._get_argument("clipboard_autosync", self.ClipboardAutosync, condition=lambda x: not x)
        # cleanup=false chỉ phát khi False (server default true)
        yield self._get_argument("cleanup", self.Cleanup, condition=lambda x: not x)
        # tunnel_forward=true chỉ phát khi True (server default false)
        yield self._get_argument("tunnel_forward", self.TunnelForward, condition=lambda x: x)
        yield self._get_argument("max_size", self.MaxSize, condition=lambda x: x > 0)
        yield self._get_argument("screen_off_timeout", self.ScreenOffTimeout, condition=lambda x: x != -1)
        yield self._get_argument(
            "new_display", self.NewDisplay,
            condition=lambda x: x is not None and bool(str(x).strip()),
        )
        # 2 option dưới đây chỉ có nghĩa ở dạng phủ định nên phát tay, giống C#
        if not self.VdSystemDecorations:
            yield "vd_system_decorations=false"
        if not self.VdDestroyContent:
            yield "vd_destroy_content=false"
        if self.DisplayImePolicy is not None:
            yield f"display_ime_policy={self.DisplayImePolicy.name.lower()}"
        yield self._get_argument("keep_active", self.KeepActive, condition=lambda x: x)
        if self.IsVideo:
            yield self._get_argument(
                "video_source", self.VideoSource,
                condition=lambda x: x != VideoSource.Display,
                formatter=lambda x: x.name.lower(),
            )

    def get_arguments(self) -> Iterable[str]:
        if self.AndroidConfig is None: self.AndroidConfig = AndroidConfig()
        if self.AudioConfig is None: self.AudioConfig = AudioConfig()

        arguments = list(self._get_server_arguments())
        arguments.extend(self.AndroidConfig.get_arguments())
        arguments.extend(self.AudioConfig.get_arguments())

        if self.IsVideo:
            if self.VideoSource == VideoSource.Camera:
                if self.CameraConfig is None: self.CameraConfig = CameraConfig()
                arguments.extend(self.CameraConfig.get_arguments())
            elif self.VideoSource == VideoSource.Display:
                if self.VideoConfig is None: self.VideoConfig = VideoConfig()
                arguments.extend(self.VideoConfig.get_arguments())

        return filter(None, arguments)
