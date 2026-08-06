# Mirror ListSupport/ListSupportQuery.cs

from typing import Iterable
from ..Configs.BaseConfig import BaseConfig
from ..Configs.ScrcpyDeployConfig import ScrcpyDeployConfig
from .. import Constant


class ListSupportQuery(BaseConfig):

    def __init__(self):
        # adb ở đâu, đẩy jar nào, jar nằm ở đâu trên thiết bị.
        # Truyền cùng instance với ScrcpyConfig.DeployConfig để query này chạy đúng cái jar mà
        # Connect() sẽ khởi động, thay vì để lại một bản copy thứ hai ở path khác trên máy.
        self.DeployConfig: ScrcpyDeployConfig = ScrcpyDeployConfig()

        # In danh sách encoder hỗ trợ ra adb shell output
        self.ListEncoders: bool = False
        # In danh sách display
        self.ListDisplays: bool = False
        # In danh sách camera
        self.ListCameras: bool = False
        # In danh sách kích thước camera
        self.ListCameraSizes: bool = False
        # In danh sách app đã cài (scrcpy 3.0+)
        self.ListApps: bool = False

    def get_arguments(self) -> Iterable[str]:
        yield Constant.ScrcpyServerVersion
        yield self._get_argument("list_encoders", self.ListEncoders, condition=lambda x: x)
        yield self._get_argument("list_displays", self.ListDisplays, condition=lambda x: x)
        yield self._get_argument("list_cameras", self.ListCameras, condition=lambda x: x)
        yield self._get_argument("list_camera_sizes", self.ListCameraSizes, condition=lambda x: x)
        yield self._get_argument("list_apps", self.ListApps, condition=lambda x: x)
