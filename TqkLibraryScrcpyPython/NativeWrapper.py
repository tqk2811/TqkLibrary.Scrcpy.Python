import ctypes
from ctypes import *
import platform
from .Configs import ScrcpyNativeConfig
import os

try:
    if platform.system() == "Windows":
        dir = os.path.dirname(os.path.abspath(__file__)) + "\\x64"
        _scrcpy_native_dll = ctypes.CDLL(dir + "\\TqkLibrary.ScrcpyNative.dll")
        _avutil = ctypes.CDLL(dir + "\\avutil-57.dll")
    else:
        raise Exception("Không hỗ trợ")
except OSError as e:
    print(f"Lỗi khi load DLL '{DLL_NAME}': {e}")
    _scrcpy_native_dll = None
    _avutil = None
    
# Delegate (C#) -> CFUNCTYPE (Python)
NativeOnDisconnectDelegate = CFUNCTYPE(None)
NativeOnClipboardReceivedDelegate = CFUNCTYPE(None, c_void_p, c_int) # IntPtr, int
NativeOnClipboardAcknowledgementDelegate = CFUNCTYPE(None, c_longlong) # long
NativeUhdiOutputDelegate = CFUNCTYPE(None, c_ushort, c_ushort, c_void_p) # UInt16, UInt16, IntPtr


# --- KHAI BÁO HÀM (DllImport) ---

if _scrcpy_native_dll:
    ## Region Scrcpy

    # [DllImport("TqkLibrary.ScrcpyNative.dll", CharSet = CharSet.Unicode, CallingConvention = CallingConvention.Cdecl)]
    # internal static extern byte FFmpegHWSupport(byte bHWSupport);
    FFmpegHWSupport = _scrcpy_native_dll.FFmpegHWSupport
    FFmpegHWSupport.argtypes = [c_byte]
    FFmpegHWSupport.restype = c_byte

    # [DllImport("TqkLibrary.ScrcpyNative.dll", CharSet = CharSet.Unicode, CallingConvention = CallingConvention.Cdecl)]
    # internal static extern IntPtr ScrcpyAlloc(string deviceId);
    ScrcpyAlloc = _scrcpy_native_dll.ScrcpyAlloc
    ScrcpyAlloc.argtypes = [c_wchar_p]
    ScrcpyAlloc.restype = c_void_p # IntPtr (Trỏ đến struct Scrcpy)

    # [DllImport("TqkLibrary.ScrcpyNative.dll", CharSet = CharSet.Unicode, CallingConvention = CallingConvention.Cdecl)]
    # internal static extern void ScrcpyFree(IntPtr scrcpy);
    ScrcpyFree = _scrcpy_native_dll.ScrcpyFree
    ScrcpyFree.argtypes = [c_void_p]
    ScrcpyFree.restype = None

    # [DllImport("TqkLibrary.ScrcpyNative.dll", CharSet = CharSet.Unicode, CallingConvention = CallingConvention.Cdecl)]
    # internal static extern bool ScrcpyConnect(IntPtr scrcpy, ref ScrcpyNativeConfig nativeConfig);
    ScrcpyConnect = _scrcpy_native_dll.ScrcpyConnect
    ScrcpyConnect.argtypes = [c_void_p, POINTER(ScrcpyNativeConfig)]
    ScrcpyConnect.restype = c_bool

    # [DllImport("TqkLibrary.ScrcpyNative.dll", CharSet = CharSet.Unicode, CallingConvention = CallingConvention.Cdecl)]
    # internal static extern bool ScrcpyStop(IntPtr scrcpy);
    ScrcpyStop = _scrcpy_native_dll.ScrcpyStop
    ScrcpyStop.argtypes = [c_void_p]
    ScrcpyStop.restype = c_bool

    # [DllImport("TqkLibrary.ScrcpyNative.dll", CharSet = CharSet.Unicode, CallingConvention = CallingConvention.Cdecl)]
    # internal static extern bool IsHaveScrcpyInstance(IntPtr scrcpy);
    IsHaveScrcpyInstance = _scrcpy_native_dll.IsHaveScrcpyInstance
    IsHaveScrcpyInstance.argtypes = [c_void_p]
    IsHaveScrcpyInstance.restype = c_bool

    # [DllImport("TqkLibrary.ScrcpyNative.dll", CharSet = CharSet.Unicode, CallingConvention = CallingConvention.Cdecl)]
    # internal static extern bool ScrcpyGetScreenSize(IntPtr scrcpy, ref int w, ref int h);
    ScrcpyGetScreenSize = _scrcpy_native_dll.ScrcpyGetScreenSize
    ScrcpyGetScreenSize.argtypes = [c_void_p, POINTER(c_int32), POINTER(c_int32)]
    ScrcpyGetScreenSize.restype = c_bool

    # [DllImport("TqkLibrary.ScrcpyNative.dll", CharSet = CharSet.Unicode, CallingConvention = CallingConvention.Cdecl)]
    # internal static extern bool ScrcpyGetDeviceName(IntPtr scrcpy, [In][Out][MarshalAs(UnmanagedType.LPArray)] byte[] buffer, int sizeInByte);
    ScrcpyGetDeviceName = _scrcpy_native_dll.ScrcpyGetDeviceName
    ScrcpyGetDeviceName.argtypes = [c_void_p, POINTER(c_ubyte), c_int32]
    ScrcpyGetDeviceName.restype = c_bool

    # [DllImport("TqkLibrary.ScrcpyNative.dll", CharSet = CharSet.Unicode, CallingConvention = CallingConvention.Cdecl)]
    # internal static extern bool ScrcpyControlCommand(IntPtr scrcpy, [In][MarshalAs(UnmanagedType.LPArray)] byte[] command, int sizeInByte);
    ScrcpyControlCommand = _scrcpy_native_dll.ScrcpyControlCommand
    ScrcpyControlCommand.argtypes = [c_void_p, POINTER(c_ubyte), c_int32]
    ScrcpyControlCommand.restype = c_bool

    # [DllImport("TqkLibrary.ScrcpyNative.dll", CharSet = CharSet.Unicode, CallingConvention = CallingConvention.Cdecl)]
    # internal static extern bool ScrcpyGetScreenShot(IntPtr scrcpy, IntPtr buffer, int sizeInByte, int w, int h, int lineSize, SwsFlag swsFlag = SwsFlag.SWS_FAST_BILINEAR);
    ScrcpyGetScreenShot = _scrcpy_native_dll.ScrcpyGetScreenShot
    ScrcpyGetScreenShot.argtypes = [c_void_p, c_void_p, c_int32, c_int32, c_int32, c_int32, c_uint32]
    ScrcpyGetScreenShot.restype = c_bool

    # [DllImport("TqkLibrary.ScrcpyNative.dll", CharSet = CharSet.Unicode, CallingConvention = CallingConvention.Cdecl)]
    # internal static extern long ScrcpyReadAudioFrame(IntPtr scrcpy, IntPtr pFrame, long last_pts, UInt32 waitFrameTime);//return current pts if > 0
    ScrcpyReadAudioFrame = _scrcpy_native_dll.ScrcpyReadAudioFrame
    ScrcpyReadAudioFrame.argtypes = [c_void_p, c_void_p, c_longlong, c_uint32]
    ScrcpyReadAudioFrame.restype = c_longlong

    ## Region Register Event
    
    # [DllImport("TqkLibrary.ScrcpyNative.dll", CharSet = CharSet.Unicode, CallingConvention = CallingConvention.Cdecl)]
    # private static extern bool RegisterClipboardEvent(IntPtr scrcpy, IntPtr nativeOnClipboardReceivedDelegate);
    # internal static bool RegisterClipboardEvent(this Scrcpy scrcpy, NativeOnClipboardReceivedDelegate onClipboardReceivedDelegate)
    # {
    #     IntPtr pointer = Marshal.GetFunctionPointerForDelegate(onClipboardReceivedDelegate);
    #     return RegisterClipboardEvent(scrcpy.Handle, pointer);
    # }
    RegisterClipboardEvent = _scrcpy_native_dll.RegisterClipboardEvent
    RegisterClipboardEvent.argtypes = [c_void_p, NativeOnClipboardReceivedDelegate]
    RegisterClipboardEvent.restype = c_bool

    # [DllImport("TqkLibrary.ScrcpyNative.dll", CharSet = CharSet.Unicode, CallingConvention = CallingConvention.Cdecl)]
    # private static extern bool RegisterClipboardAcknowledgementEvent(IntPtr scrcpy, IntPtr clipboardAcknowledgementDelegate);
    # internal static bool RegisterClipboardAcknowledgementEvent(this Scrcpy scrcpy, NativeOnClipboardAcknowledgementDelegate clipboardAcknowledgementDelegate)
    # {
    #     IntPtr pointer = Marshal.GetFunctionPointerForDelegate(clipboardAcknowledgementDelegate);
    #     return RegisterClipboardAcknowledgementEvent(scrcpy.Handle, pointer);
    # }
    RegisterClipboardAcknowledgementEvent = _scrcpy_native_dll.RegisterClipboardAcknowledgementEvent
    RegisterClipboardAcknowledgementEvent.argtypes = [c_void_p, NativeOnClipboardAcknowledgementDelegate]
    RegisterClipboardAcknowledgementEvent.restype = c_bool
    
    # [DllImport("TqkLibrary.ScrcpyNative.dll", CharSet = CharSet.Unicode, CallingConvention = CallingConvention.Cdecl)]
    # private static extern bool RegisterDisconnectEvent(IntPtr scrcpy, IntPtr delegateHandle);
    # internal static bool RegisterDisconnectEvent(this Scrcpy scrcpy, NativeOnDisconnectDelegate onDisconnectDelegate)
    # {
    #     IntPtr pointer = Marshal.GetFunctionPointerForDelegate(onDisconnectDelegate);
    #     return RegisterDisconnectEvent(scrcpy.Handle, pointer);
    # }
    RegisterDisconnectEvent = _scrcpy_native_dll.RegisterDisconnectEvent
    RegisterDisconnectEvent.argtypes = [c_void_p, NativeOnDisconnectDelegate]
    RegisterDisconnectEvent.restype = c_bool

    # [DllImport("TqkLibrary.ScrcpyNative.dll", CharSet = CharSet.Unicode, CallingConvention = CallingConvention.Cdecl)]
    # private static extern bool RegisterUhdiOutputEvent(IntPtr scrcpy, IntPtr uhdiOutputDelegate);
    # internal static bool RegisterUhdiOutputEvent(this Scrcpy scrcpy, NativeUhdiOutputDelegate uhdiOutputDelegate)
    # {
    #     IntPtr pointer = Marshal.GetFunctionPointerForDelegate(uhdiOutputDelegate);
    #     return RegisterUhdiOutputEvent(scrcpy.Handle, pointer);
    # }
    RegisterUhdiOutputEvent = _scrcpy_native_dll.RegisterUhdiOutputEvent
    RegisterUhdiOutputEvent.argtypes = [c_void_p, NativeUhdiOutputDelegate]
    RegisterUhdiOutputEvent.restype = c_bool

    # [DllImport("TqkLibrary.ScrcpyNative.dll", CharSet = CharSet.Unicode, CallingConvention = CallingConvention.Cdecl)]
    # internal static extern IntPtr D3DImageViewAlloc();
    D3DImageViewAlloc = _scrcpy_native_dll.D3DImageViewAlloc
    D3DImageViewAlloc.argtypes = []
    D3DImageViewAlloc.restype = c_void_p
    
    # [DllImport("TqkLibrary.ScrcpyNative.dll", CharSet = CharSet.Unicode, CallingConvention = CallingConvention.Cdecl)]
    # internal static extern void D3DImageViewFree(IntPtr d3dView);
    D3DImageViewFree = _scrcpy_native_dll.D3DImageViewFree
    D3DImageViewFree.argtypes = [c_void_p]
    D3DImageViewFree.restype = None
    
    # [DllImport("TqkLibrary.ScrcpyNative.dll", CharSet = CharSet.Unicode, CallingConvention = CallingConvention.Cdecl)]
    # internal static extern bool D3DImageViewRender(IntPtr d3dView, IntPtr scrcpy, IntPtr surface, bool isNewSurface, ref bool isNewtargetView);
    D3DImageViewRender = _scrcpy_native_dll.D3DImageViewRender
    D3DImageViewRender.argtypes = [c_void_p, c_void_p, c_void_p, c_bool, POINTER(c_bool)]
    D3DImageViewRender.restype = c_bool


if _avutil:
    av_frame_alloc = _avutil.av_frame_alloc
    av_frame_alloc.argtypes = []
    av_frame_alloc.restype = c_void_p
    
    av_frame_free = _avutil.av_frame_free
    av_frame_free.argtypes = [c_void_p]
    av_frame_free.restype = None
