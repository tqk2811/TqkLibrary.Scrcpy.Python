# TqkLibrary.Scrcpy.Python/Configs/ScrcpyNativeConfig.py

import ctypes
from typing import Optional
from ..Enums.FFmpegAVHWDeviceType import FFmpegAVHWDeviceType
from ..Enums.D3D11Filter import D3D11Filter

# Khớp struct ScrcpyNativeConfig của C++ (branch v4.0).
# Layout:
#   BYTE  HwType                    (1)
#   bool  IsControl                 (1)
#   bool  IsUseD3D11ForUiRender     (1)
#   bool  IsUseD3D11ForConvert      (1)
#   bool  IsAudio                   (1)
#   bool  IsVideo                   (1)
#   --- pad to align next int (2 bytes) ---
#   INT32 ConnectionTimeout         (4)
#   D3D11_FILTER Filter             (4, uint)
#   BOOL   IsForceUiGpuFlush        (4)  // BOOL = 4 bytes (Windows BOOL, không phải bool 1 byte)
#
# GpuThreadX/GpuThreadY đã bị xoá khỏi struct C++ ở commit 7f669e3 (branch 2.4 và 4.0). Giữ lại
# 2 field đó ở đây sẽ đẩy IsForceUiGpuFlush lệch 8 byte mà ctypes không hề báo lỗi.

class ScrcpyNativeConfig(ctypes.Structure):
    _fields_ = [
        ("HwType", ctypes.c_ubyte),
        ("IsControl", ctypes.c_ubyte),
        ("IsUseD3D11ForUiRender", ctypes.c_ubyte),
        ("IsUseD3D11ForConvert", ctypes.c_ubyte),
        ("IsAudio", ctypes.c_ubyte),
        ("IsVideo", ctypes.c_ubyte),
        ("ConnectionTimeout", ctypes.c_int32),
        ("Filter", ctypes.c_uint32),
        ("IsForceUiGpuFlush", ctypes.c_int32),
    ]


# Chốt layout ngay lúc import: sai ABI là lỗi ngầm, phát hiện càng sớm càng rẻ.
assert ctypes.sizeof(ScrcpyNativeConfig) == 20, (
    f"ScrcpyNativeConfig layout mismatch: {ctypes.sizeof(ScrcpyNativeConfig)} != 20 bytes"
)
