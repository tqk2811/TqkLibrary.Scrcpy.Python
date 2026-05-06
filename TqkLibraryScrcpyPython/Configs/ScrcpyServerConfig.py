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
        self.ScrcpyServerVersion: str = "2.4"  # do not change

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
