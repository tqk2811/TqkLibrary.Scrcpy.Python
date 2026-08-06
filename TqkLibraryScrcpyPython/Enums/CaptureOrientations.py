# Tên file gốc: CaptureOrientations.cs
from enum import Enum


class CaptureOrientations(Enum):
    """Giá trị capture_orientation của scrcpy 3.0.

    Lưu ý: KHÔNG dùng được .name.lower() mặc định của BaseConfig — Orient90 phải ra "90",
    Flip90 phải ra "flip90". Dùng CaptureOrientations.to_option().
    """
    Orient0 = 0
    Orient90 = 1
    Orient180 = 2
    Orient270 = 3
    Flip0 = 4
    Flip90 = 5
    Flip180 = 6
    Flip270 = 7

    def to_option(self) -> str:
        """Chuỗi truyền cho server, mirror CaptureOrientationToString() bên C#."""
        return _OPTION_NAMES[self]


_OPTION_NAMES = {
    CaptureOrientations.Orient0: "0",
    CaptureOrientations.Orient90: "90",
    CaptureOrientations.Orient180: "180",
    CaptureOrientations.Orient270: "270",
    CaptureOrientations.Flip0: "flip0",
    CaptureOrientations.Flip90: "flip90",
    CaptureOrientations.Flip180: "flip180",
    CaptureOrientations.Flip270: "flip270",
}
