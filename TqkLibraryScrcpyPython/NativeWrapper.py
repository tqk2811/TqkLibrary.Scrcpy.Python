import ctypes
from ctypes import *
import platform
from .Configs import ScrcpyNativeConfig
import os

import glob

if platform.system() != "Windows":
    raise RuntimeError("TqkLibrary.ScrcpyNative chi ho tro Windows")

_dll_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "x64")
_scrcpy_native_path = os.path.join(_dll_dir, "TqkLibrary.ScrcpyNative.dll")

# Đảm bảo Windows tìm được FFmpeg deps (avcodec, avutil, swscale, swresample, ...)
# trong cùng thư mục với ScrcpyNative.dll
if hasattr(os, "add_dll_directory"):
    os.add_dll_directory(_dll_dir)

try:
    _scrcpy_native_dll = ctypes.CDLL(_scrcpy_native_path)
except OSError as e:
    raise RuntimeError(
        f"Failed to load TqkLibrary.ScrcpyNative.dll at {_scrcpy_native_path}: {e}"
    ) from e

# Tìm avutil-*.dll (version theo FFmpeg build), load nếu có
_avutil = None
_avutil_candidates = glob.glob(os.path.join(_dll_dir, "avutil-*.dll"))
if _avutil_candidates:
    try:
        _avutil = ctypes.CDLL(_avutil_candidates[0])
    except OSError:
        _avutil = None

# Windows SOCKET là UINT_PTR (pointer-sized). Dùng c_void_p để pass socket.fileno().
SOCKET = c_void_p
INVALID_SOCKET = c_void_p(-1)

# Delegate (C++) -> CFUNCTYPE (Python). Tất cả delegate giờ trả bool về native.
NativeOnDisconnectDelegate = CFUNCTYPE(c_bool, c_int)
NativeOnClipboardReceivedDelegate = CFUNCTYPE(c_bool, c_void_p, c_int)
NativeOnClipboardAcknowledgementDelegate = CFUNCTYPE(c_bool, c_uint64)
NativeUhdiOutputDelegate = CFUNCTYPE(c_bool, c_uint16, c_uint16, c_void_p)


import warnings


def _bind(dll, name, argtypes, restype):
    """Bind 1 export. Tra None neu DLL khong co (DLL cu chua rebuild)."""
    if dll is None:
        return None
    try:
        f = getattr(dll, name)
    except AttributeError:
        warnings.warn(
            f"[NativeWrapper] Function '{name}' not found in DLL "
            f"-- need to rebuild DLL from branch v2.4 HEAD.",
            RuntimeWarning,
            stacklevel=2,
        )
        return None
    f.argtypes = argtypes
    f.restype = restype
    return f


# --- ScrcpyNative DLL bindings ---

FFmpegHWSupport = _bind(_scrcpy_native_dll, "FFmpegHWSupport", [c_byte], c_byte)

ScrcpyAlloc = _bind(_scrcpy_native_dll, "ScrcpyAlloc", [], c_void_p)

ScrcpyFree = _bind(_scrcpy_native_dll, "ScrcpyFree", [c_void_p], None)

# bool ScrcpyConnect(Scrcpy*, const ScrcpyNativeConfig&, SOCKET, SOCKET, SOCKET)
ScrcpyConnect = _bind(
    _scrcpy_native_dll, "ScrcpyConnect",
    [c_void_p, POINTER(ScrcpyNativeConfig), SOCKET, SOCKET, SOCKET],
    c_bool,
)

ScrcpyStop = _bind(_scrcpy_native_dll, "ScrcpyStop", [c_void_p], None)

IsHaveScrcpyInstance = _bind(_scrcpy_native_dll, "IsHaveScrcpyInstance", [c_void_p], c_bool)

ScrcpyGetScreenSize = _bind(
    _scrcpy_native_dll, "ScrcpyGetScreenSize",
    [c_void_p, POINTER(c_int32), POINTER(c_int32)],
    c_bool,
)

ScrcpyControlCommand = _bind(
    _scrcpy_native_dll, "ScrcpyControlCommand",
    [c_void_p, POINTER(c_ubyte), c_int32],
    c_bool,
)

# bool ScrcpyGetScreenShot(Scrcpy*, BYTE* buffer, int sizeInByte, int w, int h, int lineSize, INT32 swsFlag)
ScrcpyGetScreenShot = _bind(
    _scrcpy_native_dll, "ScrcpyGetScreenShot",
    [c_void_p, c_void_p, c_int32, c_int32, c_int32, c_int32, c_int32],
    c_bool,
)

# INT64 ScrcpyReadAudioFrame(Scrcpy*, AVFrame*, INT64 last_pts, DWORD waitFrameTime)
ScrcpyReadAudioFrame = _bind(
    _scrcpy_native_dll, "ScrcpyReadAudioFrame",
    [c_void_p, c_void_p, c_longlong, c_uint32],
    c_longlong,
)

# INT64 ScrcpyReadAudioRaw(Scrcpy*, BYTE*, INT32, INT32, INT32, INT32, INT64, DWORD, INT32*)
ScrcpyReadAudioRaw = _bind(
    _scrcpy_native_dll, "ScrcpyReadAudioRaw",
    [c_void_p, POINTER(c_ubyte), c_int32, c_int32, c_int32, c_int32, c_longlong, c_uint32, POINTER(c_int32)],
    c_longlong,
)

RegisterClipboardEvent = _bind(
    _scrcpy_native_dll, "RegisterClipboardEvent",
    [c_void_p, NativeOnClipboardReceivedDelegate],
    c_bool,
)

RegisterClipboardAcknowledgementEvent = _bind(
    _scrcpy_native_dll, "RegisterClipboardAcknowledgementEvent",
    [c_void_p, NativeOnClipboardAcknowledgementDelegate],
    c_bool,
)

RegisterDisconnectEvent = _bind(
    _scrcpy_native_dll, "RegisterDisconnectEvent",
    [c_void_p, NativeOnDisconnectDelegate],
    c_bool,
)

RegisterUhdiOutputEvent = _bind(
    _scrcpy_native_dll, "RegisterUhdiOutputEvent",
    [c_void_p, NativeUhdiOutputDelegate],
    c_bool,
)

# D3D image view
D3DImageViewAlloc = _bind(_scrcpy_native_dll, "D3DImageViewAlloc", [], c_void_p)
D3DImageViewFree = _bind(_scrcpy_native_dll, "D3DImageViewFree", [c_void_p], None)
D3DImageViewRender = _bind(
    _scrcpy_native_dll, "D3DImageViewRender",
    [c_void_p, c_void_p, c_void_p, c_bool, POINTER(c_bool)],
    c_bool,
)


# --- avutil DLL bindings ---

av_frame_alloc = _bind(_avutil, "av_frame_alloc", [], c_void_p)
av_frame_free = _bind(_avutil, "av_frame_free", [c_void_p], None)
