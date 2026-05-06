# TqkLibrary.Scrcpy.Python/Configs/CameraConfig.py

from typing import Optional, Iterable
from .BaseConfig import BaseConfig
from ..Structs.Size import Size 
from ..Enums.CameraFacing import CameraFacing 

class CameraConfig(BaseConfig):

    def __init__(self):
        self.CameraId: Optional[int] = None
        self.CameraSize: Optional[Size] = None
        self.CameraFacing: CameraFacing = CameraFacing.Any
        self.CameraAr: Optional[str] = None
        self.Camerafps: int = 0
        self.CameraHighSpeed: bool = False

    def get_arguments(self) -> Iterable[str]:
        # --camera-id (C# default condition: not None/0)
        yield self._get_argument("camera_id", self.CameraId)
        
        # --camera-size (C# default condition: not None)
        yield self._get_argument("camera_size", self.CameraSize)
        
        # --camera-facing (C# condition: x != CameraFacing.Any; Formatter: x.ToString().ToLower())
        yield self._get_argument(
            "camera_facing", 
            self.CameraFacing,
            condition=lambda x: x != CameraFacing.Any
            # Formatter đã được xử lý trong BaseConfig cho Enum.
        )
        
        # --camera-ar (C# condition: !string.IsNullOrWhiteSpace)
        yield self._get_argument(
            "camera_ar", 
            self.CameraAr, 
            condition=lambda x: bool(x and str(x).strip())
        )
        
        # --camera-fps (C# condition: x > 0)
        yield self._get_argument(
            "camera_fps", 
            self.Camerafps, 
            condition=lambda x: x > 0
        )
        
        # --camera-high-speed (C# default condition: value == true)
        yield self._get_argument("camera_high_speed", self.CameraHighSpeed)