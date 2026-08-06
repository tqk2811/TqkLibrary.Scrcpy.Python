# TqkLibrary.Scrcpy.Python/Configs/ScrcpyConfig.py
from .ScrcpyServerConfig import ScrcpyServerConfig
from .ScrcpyNativeConfig import ScrcpyNativeConfig
from .ScrcpyDeployConfig import ScrcpyDeployConfig
from .ClientConfig import ClientConfig
from .AudioConfig import AudioConfig


class ScrcpyConfig:
    """Config cấp cao nhất, gom 3 nhóm tách bạch:

    - ServerConfig : tham số gửi cho scrcpy server chạy trên thiết bị
    - DeployConfig : cách tới được thiết bị (adb, jar, timeout kết nối)
    - ClientConfig : giải mã/render phía PC
    """

    def __init__(self):
        self.ServerConfig: ScrcpyServerConfig = ScrcpyServerConfig()

        # Mọi thứ để tới được thiết bị: adb ở đâu, đẩy jar nào, jar nằm ở đâu trên thiết bị,
        # có push lại mỗi lần Connect hay không, và chờ kết nối bao lâu. Cũng là nguồn duy nhất
        # của đường dẫn adb dùng khi connect (reverse tunnel, chạy server) nên client và deploy
        # không thể lệch nhau. Truyền chính instance này vào Scrcpy.PushServer() khi push tay.
        self.DeployConfig: ScrcpyDeployConfig = ScrcpyDeployConfig()

        # Tuỳ chọn giải mã/render phía client, không gửi gì xuống thiết bị.
        self.ClientConfig: ClientConfig = ClientConfig()

    def __str__(self) -> str:
        if self.ServerConfig is None:
            self.ServerConfig = ScrcpyServerConfig()
        return " ".join(self.ServerConfig.get_arguments())

    def NativeConfig(self) -> ScrcpyNativeConfig:
        if self.ServerConfig is None:
            self.ServerConfig = ScrcpyServerConfig()
        if self.DeployConfig is None:
            self.DeployConfig = ScrcpyDeployConfig()
        if self.ClientConfig is None:
            self.ClientConfig = ClientConfig()
        server_config = self.ServerConfig
        client_config = self.ClientConfig

        if server_config.AudioConfig is None:
            server_config.AudioConfig = AudioConfig()

        is_video = server_config.IsVideo
        is_audio = server_config.AudioConfig.IsAudio
        is_control = server_config.IsControl
        if not (is_video or is_audio or is_control):
            raise ValueError("At least one stream (video, audio, control) must be enabled.")

        return ScrcpyNativeConfig(
            HwType=client_config.HwType.value,
            IsControl=is_control,
            IsUseD3D11ForUiRender=client_config.IsUseD3D11ForUiRender,
            IsUseD3D11ForConvert=client_config.IsUseD3D11ForConvert,
            IsAudio=is_audio,
            IsVideo=is_video,
            ConnectionTimeout=self.DeployConfig.ConnectionTimeout,
            Filter=client_config.Filter.value,
            IsForceUiGpuFlush=int(bool(client_config.IsForceUiGpuFlush)),
        )
