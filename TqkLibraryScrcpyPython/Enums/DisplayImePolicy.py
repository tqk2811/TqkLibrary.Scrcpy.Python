# Tên file gốc: DisplayImePolicy.cs
from enum import Enum


class DisplayImePolicy(Enum):
    """Chính sách IME trên display được capture (scrcpy 3.2, --display-ime-policy)."""

    # Hiện IME trên chính display đang capture
    Local = 0
    # Hiện IME trên display mặc định (fallback)
    Fallback = 1
    # Ẩn IME
    Hide = 2
