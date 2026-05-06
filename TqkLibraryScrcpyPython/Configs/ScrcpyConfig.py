# TqkLibrary.Scrcpy.Python/Configs/ScrcpyConfig.py
from .ScrcpyServerConfig import ScrcpyServerConfig
from .ScrcpyNativeConfig import ScrcpyNativeConfig
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
        """Tạo chuỗi tham số scrcpy hoàn chỉnh."""
        if self.ServerConfig is None:
            self.ServerConfig = ScrcpyServerConfig()
        
        # Lấy tham số từ ServerConfig (đã kế thừa BaseConfig và gọi get_arguments())
        arguments = self.ServerConfig.get_arguments()
        return " ".join(arguments)
        
    def NativeConfig(self) -> ScrcpyNativeConfig:
        configure_arguments = str(self)
        gpu_thread_x = max(1, min(self.GpuThreadX, 32))
        gpu_thread_y = max(1, min(self.GpuThreadY, 32))
        server_config = self.ServerConfig
        if server_config is None:
             server_config = ScrcpyServerConfig()
             self.ServerConfig = server_config # Cập nhật lại thuộc tính
             
        audio_config = server_config.AudioConfig
        if audio_config is None:
            audio_config = AudioConfig()
            server_config.AudioConfig = audio_config # Cập nhật lại thuộc tính

        hw_type_value = 0
        # Tạo và điền dữ liệu vào struct ScrcpyNativeConfig
        return ScrcpyNativeConfig(
            HwType=self.HwType.value,
            ForceAdbForward=server_config.TunnelForward,
            IsControl=server_config.IsControl,
            IsUseD3D11ForUiRender=self.IsUseD3D11ForUiRender,
            IsUseD3D11ForConvert=self.IsUseD3D11ForConvert,
            IsAudio=audio_config.IsAudio,
            ScrcpyServerPath=self.ScrcpyServerPath,
            AdbPath=self.AdbPath,
            ConfigureArguments=configure_arguments,
            ConnectionTimeout=self.ConnectionTimeout,
            Filter=self.Filter.value,
            SCID=server_config.SCID,
            GpuThreadX=gpu_thread_x,
            GpuThreadY=gpu_thread_y,
            IsForceUiGpuFlush = self.IsForceUiGpuFlush,
        )