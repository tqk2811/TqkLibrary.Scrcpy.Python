# Tên file gốc: CaptureOrientationLock.cs
from enum import Enum


class CaptureOrientationLock(Enum):
    """Chế độ khoá cho capture_orientation (scrcpy 3.0)."""

    # Không khoá — hướng thay đổi tự do
    Unlocked = 0
    # Khoá theo giá trị CaptureOrientations chỉ định (tiền tố "@")
    LockedValue = 1
    # Khoá theo hướng ban đầu của thiết bị lúc khởi động (chỉ mỗi "@")
    LockedInitial = 2
