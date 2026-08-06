# Tên file gốc: AudioSource.cs
from enum import Enum

class AudioSource(Enum):
    """
    TqkLibrary.Scrcpy.AudioSource
    """
    Auto = 0
    Output = 1
    Mic = 2
    # Thu audio đang phát của thiết bị mà không tắt tiếng thiết bị (Android 13+)
    Playback = 3