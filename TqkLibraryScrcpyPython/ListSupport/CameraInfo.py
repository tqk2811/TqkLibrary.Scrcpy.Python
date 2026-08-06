# Mirror ListSupport/CameraInfo.cs
from typing import Optional
from ..Structs.Size import Size
from ..Enums.CameraFacing import CameraFacing


class CameraInfo:
    def __init__(
            self,
            CameraId: int = 0,
            CameraFacing: CameraFacing = CameraFacing.Any,
            IsHighSpeed: bool = False,
            Size: Optional[Size] = None,
            FpsMin: int = 0,
            FpsMax: int = 0):
        self.CameraId: int = CameraId
        self.CameraFacing = CameraFacing
        self.IsHighSpeed: bool = IsHighSpeed
        self.Size = Size
        self.FpsMin: int = FpsMin
        self.FpsMax: int = FpsMax

    def __str__(self) -> str:
        size = f"{self.Size.Width}x{self.Size.Height}" if self.Size else "None"
        return (f"{self.CameraFacing.name}, Size: {size}, "
                f"IsHighSpeed: {self.IsHighSpeed}, Fps=[{self.FpsMin}-{self.FpsMax}]")

    __repr__ = __str__
