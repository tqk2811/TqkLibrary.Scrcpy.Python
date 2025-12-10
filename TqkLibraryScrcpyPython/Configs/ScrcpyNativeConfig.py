# TqkLibrary.Scrcpy.Python/Configs/ScrcpyNativeConfig.py

import ctypes
from typing import Optional
from ..Enums.FFmpegAVHWDeviceType import FFmpegAVHWDeviceType
from ..Enums.D3D11Filter import D3D11Filter

# C# type mapping to ctypes:
# U1 (UnmanagedType.U1) -> ctypes.c_ubyte (cho bool/enum 1 byte)
# LPWStr (Unicode string) -> ctypes.c_wchar_p (pointer đến chuỗi Unicode)
# int -> ctypes.c_int
# uint -> ctypes.c_uint

class ScrcpyNativeConfig(ctypes.Structure):
    """
    Mô phỏng cấu trúc ScrcpyNativeConfig của C# cho C-Interop (dùng ctypes).
    """
    _fields_ = [
        # public FFmpegAVHWDeviceType HwType; // uint8
        ("HwType", ctypes.c_ubyte), 
        
        # public bool ForceAdbForward;
        ("ForceAdbForward", ctypes.c_ubyte), 
        
        # public bool IsControl;
        ("IsControl", ctypes.c_ubyte),

        # public bool IsUseD3D11ForUiRender;
        ("IsUseD3D11ForUiRender", ctypes.c_ubyte),

        # public bool IsUseD3D11ForConvert;
        ("IsUseD3D11ForConvert", ctypes.c_ubyte),

        # public bool IsAudio;
        ("IsAudio", ctypes.c_ubyte),

        # public string AdbPath;
        ("AdbPath", ctypes.c_wchar_p),

        # public string ScrcpyServerPath;
        ("ScrcpyServerPath", ctypes.c_wchar_p),

        # public string ConfigureArguments;
        ("ConfigureArguments", ctypes.c_wchar_p),

        # public int ConnectionTimeout;
        ("ConnectionTimeout", ctypes.c_int),

        # public D3D11Filter Filter; // D3D11Filter là uint
        ("Filter", ctypes.c_uint), 

        # public int SCID;
        ("SCID", ctypes.c_int),

        # public uint GpuThreadX;
        ("GpuThreadX", ctypes.c_uint),

        # public uint GpuThreadY;
        ("GpuThreadY", ctypes.c_uint),

        # public bool IsForceUiGpuFlush;
        ("IsForceUiGpuFlush", ctypes.c_ubyte),
    ]