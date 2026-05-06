# TqkLibrary.Scrcpy.Python/Configs/ScrcpyConfig.py
from .ScrcpyServerConfig import ScrcpyServerConfig
from .ScrcpyNativeConfig import ScrcpyNativeConfig
from .AudioConfig import AudioConfig
from ..Enums.FFmpegAVHWDeviceType import FFmpegAVHWDeviceType
from ..Enums.D3D11Filter import D3D11Filter


class ScrcpyConfig:

    def __init__(self):
        self.ServerConfig: ScrcpyServerConfig = ScrcpyServerConfig()
        self.AdbPath: str = "adb.exe"
        self.ScrcpyServerPath: str = "scrcpy-server.jar"
        self.ConnectionTimeout: int = 3000
        self.HwType: FFmpegAVHWDeviceType = FFmpegAVHWDeviceType.AV_HWDEVICE_TYPE_NONE
        self.Filter: D3D11Filter = D3D11Filter.D3D11_FILTER_MIN_MAG_LINEAR_MIP_POINT
        self.IsUseD3D11ForUiRender: bool = False
        self.IsUseD3D11ForConvert: bool = False
        self.GpuThreadX: int = 1
        self.GpuThreadY: int = 4
        self.IsForceUiGpuFlush: bool = False

    def __str__(self) -> str:
        if self.ServerConfig is None:
            self.ServerConfig = ScrcpyServerConfig()
        return " ".join(self.ServerConfig.get_arguments())

    def NativeConfig(self) -> ScrcpyNativeConfig:
        if self.ServerConfig is None:
            self.ServerConfig = ScrcpyServerConfig()
        server_config = self.ServerConfig

        if server_config.AudioConfig is None:
            server_config.AudioConfig = AudioConfig()

        is_video = server_config.IsVideo
        is_audio = server_config.AudioConfig.IsAudio
        is_control = server_config.IsControl
        if not (is_video or is_audio or is_control):
            raise ValueError("At least one stream (video, audio, control) must be enabled.")

        gpu_thread_x = max(1, min(self.GpuThreadX, 32))
        gpu_thread_y = max(1, min(self.GpuThreadY, 32))

        return ScrcpyNativeConfig(
            HwType=self.HwType.value,
            IsControl=is_control,
            IsUseD3D11ForUiRender=self.IsUseD3D11ForUiRender,
            IsUseD3D11ForConvert=self.IsUseD3D11ForConvert,
            IsAudio=is_audio,
            IsVideo=is_video,
            ConnectionTimeout=self.ConnectionTimeout,
            Filter=self.Filter.value,
            GpuThreadX=gpu_thread_x,
            GpuThreadY=gpu_thread_y,
            IsForceUiGpuFlush=int(bool(self.IsForceUiGpuFlush)),
        )
