# TqkLibrary.Scrcpy.Python/Configs/ScrcpyServerConfig.py

from typing import Optional, Iterable
from .BaseConfig import BaseConfig
from .AndroidConfig import AndroidConfig
from .AudioConfig import AudioConfig
from .VideoConfig import VideoConfig
from .CameraConfig import CameraConfig
from ..Enums.VideoSource import VideoSource 
from ..Enums.LogLevel import LogLevel 

class ScrcpyServerConfig(BaseConfig):

    def __init__(self):
        # Config Sub-classes
        self.AndroidConfig: Optional[AndroidConfig] = None
        self.VideoConfig: Optional[VideoConfig] = None
        self.AudioConfig: Optional[AudioConfig] = None
        self.CameraConfig: Optional[CameraConfig] = None

        # Properties
        self.VideoSource: VideoSource = VideoSource.Display
        self.IsControl: bool = True
        self.LogLevel: LogLevel = LogLevel.Info
        self.SCID: int = -1
        self.ClipboardAutosync: bool = False
        self.Cleanup: bool = False
        self.TunnelForward: bool = False  # do not change
        self.MaxSize: int = 0
        self.ScrcpyServerVersion: str = "2.4"  # do not change

    def _get_server_arguments(self) -> Iterable[str]:
        """Tạo các tham số chỉ dành cho Server Config."""        
        yield self.ScrcpyServerVersion
        yield self._get_argument("control", self.IsControl)
        yield self._get_argument("scid", self.SCID, condition=lambda x: x != -1,formatter=lambda x: f"{(x & 0x7FFFFFFF):04x}")
        yield self._get_argument("clipboard_autosync", self.ClipboardAutosync)
        yield self._get_argument("cleanup", self.Cleanup)
        yield self._get_argument("tunnel_forward", self.TunnelForward)
        yield self._get_argument("max_size", self.MaxSize, condition=lambda x: x > 0)
        yield self._get_argument("video_source", self.VideoSource, condition=lambda x: x != VideoSource.Display,formatter=lambda x: x.name.lower());

    def get_arguments(self) -> Iterable[str]:
        # Khởi tạo các config nếu chưa có
        if self.AndroidConfig is None: self.AndroidConfig = AndroidConfig()
        if self.AudioConfig is None: self.AudioConfig = AudioConfig()
        
        # Bắt đầu với các tham số của Server
        arguments = list(self._get_server_arguments())
        
        # Thêm các tham số từ Android và Audio
        arguments.extend(self.AndroidConfig.get_arguments())
        arguments.extend(self.AudioConfig.get_arguments())

        # Thêm VideoConfig hoặc CameraConfig tùy thuộc vào VideoSource
        if self.VideoSource == VideoSource.Camera:
            if self.CameraConfig is None: self.CameraConfig = CameraConfig()
            arguments.extend(self.CameraConfig.get_arguments())
        elif self.VideoSource == VideoSource.Display:
            if self.VideoConfig is None: self.VideoConfig = VideoConfig()
            arguments.extend(self.VideoConfig.get_arguments())

        # Lọc ra các giá trị None và trả về
        return filter(None, arguments)