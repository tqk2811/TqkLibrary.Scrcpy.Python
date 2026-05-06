# TqkLibrary.Scrcpy.Python/Configs/ScrcpyNativeConfig.py

import ctypes
from typing import Optional
from ..Enums.FFmpegAVHWDeviceType import FFmpegAVHWDeviceType
from ..Enums.D3D11Filter import D3D11Filter

# Khớp struct ScrcpyNativeConfig của C++ (branch v2.4 HEAD).
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
#   UINT32 GpuThreadX               (4)
#   UINT32 GpuThreadY               (4)
#   BOOL   IsForceUiGpuFlush        (4)  // BOOL = 4 bytes (Windows BOOL, không phải bool 1 byte)

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
        ("GpuThreadX", ctypes.c_uint32),
        ("GpuThreadY", ctypes.c_uint32),
        ("IsForceUiGpuFlush", ctypes.c_int32),
    ]
