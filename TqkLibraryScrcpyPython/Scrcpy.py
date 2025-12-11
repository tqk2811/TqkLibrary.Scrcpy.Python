import threading
from typing import Optional, Any
from ctypes import *
from .NativeWrapper import (
    ScrcpyAlloc, ScrcpyFree, ScrcpyConnect, ScrcpyStop,
    IsHaveScrcpyInstance, 
    ScrcpyGetScreenSize, 
    ScrcpyGetDeviceName,
    ScrcpyControlCommand, 
    ScrcpyGetScreenShot, 
    ScrcpyReadAudioFrame,
    RegisterDisconnectEvent, NativeOnDisconnectDelegate,
    RegisterClipboardEvent, NativeOnClipboardReceivedDelegate,
    RegisterClipboardAcknowledgementEvent, NativeOnClipboardAcknowledgementDelegate,
    RegisterUhdiOutputEvent, NativeUhdiOutputDelegate,
)
from .Controls import(
    ScrcpyControl
)
from .Configs import(
    ScrcpyConfig
)
from .Structs import *
from .Interfaces import *
from .Events import *
from .Enums import *
import numpy as np
import cv2

class Scrcpy(IScrcpy):
    def __init__(self, deviceId: str):
        if not deviceId:
            raise ValueError("deviceId cannot be empty or whitespace")
        
        self._deviceId = deviceId
        self._handle = c_void_p(0)

        self._lastClipboard: str = ""
        self._disconnectEvent = DisconnectEvent()
        self._clipboardEvent = ClipboardEvent()
        
        self._handle = ScrcpyAlloc(deviceId)
        self._control: ScrcpyControl = ScrcpyControl(self)#cần _handle
        self._control.OnClipboardReceived = self._control_on_clipboard_received

        self._native_on_disconnect_delegate = NativeOnDisconnectDelegate(self._on_disconnect_callback)
        if not RegisterDisconnectEvent(self._handle, self._native_on_disconnect_delegate):
            raise RuntimeError("Failed to register disconnect event.")

        self._uhdi_output_delegate = NativeUhdiOutputDelegate(self._uhdi_output_callback)
        if not RegisterUhdiOutputEvent(self._handle, self._uhdi_output_delegate):
             raise RuntimeError("Failed to register UHDI output event.")
        
        
        self._countdown_event = threading.Semaphore(1)
        self._is_disposed = False

    @property
    def DeviceId(self) -> str:
        return self._deviceId

    @property
    def DeviceName(self) -> str:
        return self._get_device_name()

    @property
    def IsConnected(self) -> bool:
        result = False
        with self._countdown_event:
            result = IsHaveScrcpyInstance(self._handle)
        return result

    @property
    def ScreenSize(self) -> Size:
        return self._get_screen_size()

    @property
    def LastClipboard(self) -> str:
        return self._lastClipboard

    @property
    def Control(self) -> ScrcpyControl:
        return self._control

    @property
    def OnDisconnect(self) -> DisconnectEvent:
        return self._disconnectEvent

    @property
    def OnClipboardReceived(self) -> ClipboardEvent:
        return self._clipboardEvent

    # --- Phương thức Chính (Public Methods) ---

    def Connect(self, config: Optional[ScrcpyConfig] = None) -> bool:
        result = False
        if config is None:
            config = ScrcpyConfig()

        native_config = config.NativeConfig()
        
        # Sử dụng semaphore để đảm bảo an toàn luồng
        with self._countdown_event:
            # Tương đương với TryAddCount & Signal
            result = ScrcpyConnect(self._handle, POINTER(type(native_config))(native_config))
        return result

    def Stop(self):
        """
        Dừng kết nối Scrcpy. Tương đương với ScrcpyStop.
        """
        if self._is_disposed:
            return

        # Dùng semaphore để đảm bảo an toàn luồng
        if self._countdown_event.acquire(blocking=False):
            try:
                ScrcpyStop(self._handle)
            finally:
                self._countdown_event.release()
    
    def GetScreenShot(self,swsFlag: Optional[SwsFlag] = None) -> Optional[np.ndarray]:
        """
        Chụp ảnh màn hình. Trong C# trả về System.Drawing.Bitmap.
        Trong Python, ta cần xử lý buffer để tạo một đối tượng hình ảnh (ví dụ: dùng PIL/Pillow).
        Do không có thư viện hình ảnh được cung cấp, ta chỉ thực hiện logic gọi native.
        """
        if self._is_disposed:
            return None

        size = self._get_screen_size()
        if size.Width <= 0 or size.Height <= 0:
            return None

        # Logic padding 16-byte (fix_size)
        width = size.Width
        fix_width = width if width % 16 == 0 else width + 16 - (width % 16)
        fix_size = Size(fix_width, size.Height)
        
        # 32bppArgb = 4 byte/pixel (A, R, G, B)
        buffer_size_in_byte = fix_size.Width * fix_size.Height * 4
        
        # Tạo buffer byte cho ảnh (tương đương với LockBits trong C#)
        # Sử dụng byte array của Python, truyền qua ctypes
        image_buffer = (c_ubyte * buffer_size_in_byte)()
        
        if swsFlag is None:
            swsFlag = SwsFlag.SWS_FAST_BILINEAR

        isSucccess : bool = False
        with self._countdown_event:
            isSucccess = ScrcpyGetScreenShot(
                self._handle,
                image_buffer, # Python buffer được truyền qua như c_void_p
                buffer_size_in_byte,
                size.Width,
                size.Height,
                fix_size.Width * 4, # lineSize
                swsFlag.value
            )

        img_array = np.frombuffer(image_buffer, dtype=np.uint8).reshape(fix_size.Height, fix_size.Width, 4)
        if size.Width != fix_size.Width:
            img_array = img_array[:size.Height, :size.Width, :]

        bgr_image = img_array[:, :, :3]
        return bgr_image

    def SendControl(self, command: bytes) -> bool:
        """
        Phương thức nội bộ để gửi lệnh điều khiển.
        Tương đương với ScrcpyControlCommand.
        """
        result = False
        
        # Chuyển bytes Python sang mảng c_ubyte (tương đương byte[] trong C#)
        c_command = (c_ubyte * len(command))(*command)

        with self._countdown_event:
            result = ScrcpyControlCommand(self._handle, c_command, len(command))

        return result


    # --- Native Register (Delegates) ---
    def _register_clipboard_event(self, method: NativeOnClipboardReceivedDelegate) -> bool:
        return RegisterClipboardEvent(self._handle, method)

    def _register_clipboard_acknowledgement_event(self, method: NativeOnClipboardAcknowledgementDelegate) -> bool:
        return RegisterClipboardAcknowledgementEvent(self._handle, method)

    # --- Native Callbacks (Delegates) ---

    def _on_disconnect_callback(self):
        """ Callback cho NativeOnDisconnectDelegate """
        # Chạy trong một luồng riêng (tương đương ThreadPool.QueueUserWorkItem)
        def run_disconnect():
            self.Stop()
            self.OnDisconnect.Fire(self)
        threading.Thread(target=run_disconnect).start()
    
    def _control_on_clipboard_received(self, control, data):
        """ Event handler từ ScrcpyControl """
        self.LastClipboard = data
        def run_fireClipboard():
            self.OnClipboardReceived.Fire(self,data) 
        threading.Thread(target=run_fireClipboard).start()

    def _uhdi_output_callback(self, id: int, size: int, buff: c_void_p):
        """ Callback cho NativeUhdiOutputDelegate """
        print(f"_uhdi_output_callback received: id {id}, size {size}")

    
    # --- Getters ---

    def _get_screen_size(self) -> Size:
        w = c_int(0)
        h = c_int(0)
        
        with self._countdown_event:
            ScrcpyGetScreenSize(self._handle, POINTER(c_int)(w), POINTER(c_int)(h))
            
        return Size(w.value, h.value)

    def _get_device_name(self) -> str:
        # Giả định max size là 64 byte (64 ký tự ASCII)
        buffer_size = 64
        buffer = (c_ubyte * buffer_size)() # byte[] buffer = new byte[64];
        
        with self._countdown_event:
            # Tương đương ScrcpyGetDeviceName(_handle, buffer, 64);
            ScrcpyGetDeviceName(self._handle, buffer, buffer_size)
            
        # Giải mã buffer thành chuỗi ASCII và loại bỏ ký tự null '\x00'
        raw_bytes = bytes(buffer)
        try:
            name = raw_bytes.decode('ascii').split('\x00', 1)[0]
        except UnicodeDecodeError:
            name = "" # Xử lý lỗi giải mã
            
        return name

    # --- Dispose (Quản lý tài nguyên) ---

    def __del__(self):
        """ Finalizer (tương đương destructor trong C#) """
        self.Dispose(False)

    def Dispose(self, disposing: bool = True):
        """
        Giải phóng tài nguyên. Tương đương với Dispose(bool disposing) trong C#.
        """
        if self._is_disposed:
            return
        
        self._is_disposed = True

        # Hủy đăng ký TerminationHandler (bỏ qua ở đây)
        
        self.Stop()
        
        # Tương đương: countdownEvent.Signal(); countdownEvent.Wait();
        # Đảm bảo các luồng đang chạy thoát
        try:
            # Acquire và release để chặn các lần gọi TryAddCount tiếp theo
            if self._countdown_event.acquire(blocking=True, timeout=5): 
                # Chờ các luồng đang sử dụng resource hoàn thành
                self._countdown_event.release() 
        except Exception:
            # Xử lý nếu chờ thất bại (ví dụ: timeout)
            pass
            
        if self._handle:
            ScrcpyFree(self._handle)
            self._handle = c_void_p(0)
        
        # Không cần Dispose Semaphore/CountdownEvent trong Python theo cách tương tự C#