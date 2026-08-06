# TqkLibrary.Scrcpy.Python/Configs/ScrcpyConfig.py
from .ScrcpyServerConfig import ScrcpyServerConfig
from .ScrcpyNativeConfig import ScrcpyNativeConfig
from .ScrcpyDeployConfig import ScrcpyDeployConfig
from .AudioConfig import AudioConfig
from ..Enums.FFmpegAVHWDeviceType import FFmpegAVHWDeviceType
from ..Enums.D3D11Filter import D3D11Filter


class ScrcpyConfig:

    def __init__(self):
        self.ServerConfig: ScrcpyServerConfig = ScrcpyServerConfig()

        # adb ở đâu, đẩy jar nào, jar nằm ở đâu trên thiết bị. Cũng là nguồn duy nhất của
        # đường dẫn adb dùng khi connect (reverse tunnel, chạy server) nên client và deploy
        # không thể lệch nhau. Truyền chính instance này vào Scrcpy.PushServer() khi push tay.
        self.DeployConfig: ScrcpyDeployConfig = ScrcpyDeployConfig()

        # Push jar lên thiết bị mỗi lần Connect. Jar nằm lại trên máy giữa các lần kết nối nên
        # push lại chỉ tốn thời gian. Đặt False để reconnect nhanh hơn — khi đó người gọi tự
        # chịu trách nhiệm jar đã có sẵn ở ScrcpyServerAndroidPath (gọi PushServer() một lần),
        # nếu không server không chạy được và Connect thất bại.
        self.ForcePush: bool = True

        self.ConnectionTimeout: int = 3000
        self.HwType: FFmpegAVHWDeviceType = FFmpegAVHWDeviceType.AV_HWDEVICE_TYPE_NONE
        self.Filter: D3D11Filter = D3D11Filter.D3D11_FILTER_MIN_MAG_LINEAR_MIP_POINT
        self.IsUseD3D11ForUiRender: bool = False
        self.IsUseD3D11ForConvert: bool = False
        self.IsForceUiGpuFlush: bool = True

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

        return ScrcpyNativeConfig(
            HwType=self.HwType.value,
            IsControl=is_control,
            IsUseD3D11ForUiRender=self.IsUseD3D11ForUiRender,
            IsUseD3D11ForConvert=self.IsUseD3D11ForConvert,
            IsAudio=is_audio,
            IsVideo=is_video,
            ConnectionTimeout=self.ConnectionTimeout,
            Filter=self.Filter.value,
            IsForceUiGpuFlush=int(bool(self.IsForceUiGpuFlush)),
        )
