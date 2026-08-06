# TqkLibrary.Scrcpy.Python/Configs/ScrcpyDeployConfig.py
# Mirror ScrcpyDeployConfig.cs

from .. import Constant


class ScrcpyDeployConfig:
    """Mọi thứ cần để tới được thiết bị và deploy scrcpy server lên đó: adb ở đâu, đẩy jar nào,
    và jar nằm ở đâu trên máy.

    Tách riêng khỏi ScrcpyConfig vì deploy là việc một lần, không cần tới các option
    video/audio/control của một phiên mirror. Dùng được độc lập với Scrcpy.PushServer().
    """

    def __init__(self):
        # Đường dẫn adb dùng cho MỌI lệnh tới thiết bị: push jar, reverse tunnel, chạy server.
        self.AdbPath: str = "adb.exe"

        # Đường dẫn jar phía PC, sẽ được push lên thiết bị.
        self.ScrcpyServerPath: str = "scrcpy-server.jar"

        # Đường dẫn jar trên thiết bị, cũng là path Connect() chạy server từ đó.
        self.ScrcpyServerAndroidPath: str = Constant.ScrcpyServerAndroidPath

    def GetResolvedAndroidPath(self) -> str:
        """ScrcpyServerAndroidPath với {ver} đã thay — path thật trên thiết bị."""
        return self.ScrcpyServerAndroidPath.replace("{ver}", Constant.ScrcpyServerVersion)
