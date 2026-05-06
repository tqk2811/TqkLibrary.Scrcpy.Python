import threading
import random
from typing import Callable, Optional, Any
from io import BytesIO
from ctypes import c_void_p, c_int, CFUNCTYPE, cast, POINTER, c_char, string_at
from .ScrcpyControlHelper import ScrcpyControlHelper, Rectangle, AndroidKeyEventAction, \
    AndroidKeyCode, AndroidKeyEventMeta, AndroidMotionEventAction, \
    AndroidMotionEventButton, ScrcpyScreenPowerMode, CopyKey

from ..Interfaces import(
    IControl,
    IScrcpy
)
from ..NativeWrapper import (
    RegisterClipboardEvent, NativeOnClipboardReceivedDelegate,
    RegisterClipboardAcknowledgementEvent, NativeOnClipboardAcknowledgementDelegate,
)

class ScrcpyControl(IControl):
    """
    Tương đương với ScrcpyControl.cs
    Đóng gói các lệnh điều khiển scrcpy và xử lý sự kiện clipboard.
    """
    _random = random.Random()

    def __init__(self, scrcpy: IScrcpy):
        self._scrcpy = scrcpy
        self._control_helper = ScrcpyControlHelper()

        self._native_on_clipboard_received_delegate = NativeOnClipboardReceivedDelegate(self._native_on_clipboard_received)
        if not self._scrcpy._register_clipboard_event(self._native_on_clipboard_received_delegate):
            raise RuntimeError("Failed to register clipboard event.")
            
        self._native_on_clipboard_acknowledgement_delegate = NativeOnClipboardAcknowledgementDelegate(self._native_clipboard_acknowledgement_received)
        if not self._scrcpy._register_clipboard_acknowledgement_event(self._native_on_clipboard_acknowledgement_delegate):
            raise RuntimeError("Failed to register clipboard acknowledgement event.")
        

    @property
    def Scrcpy(self) -> IScrcpy:
        return self._scrcpy

    def InjectKeycode(
            self,
            action: AndroidKeyEventAction,
            keycode: AndroidKeyCode,
            repeat: int = 1,
            meta_state: AndroidKeyEventMeta = 0x8000) -> bool:
        return self._send_control(self._control_helper.inject_keycode(action, keycode, repeat, meta_state))

    def InjectText(self, text: str) -> bool:
        return self._send_control(self._control_helper.inject_text(text))

    def InjectTouchEvent(
            self,
            action: AndroidMotionEventAction,
            pointer_id: int,
            position: Rectangle,
            pressure: float,
            buttons: AndroidMotionEventButton,
            action_button: AndroidMotionEventButton) -> bool:
        return self._send_control(self._control_helper.inject_touch_event(action, pointer_id, position, pressure, buttons, action_button))

    def InjectScrollEvent(self, position: Rectangle, v_scroll: float, h_scroll: float = 0, button: AndroidMotionEventButton = 1) -> bool: # BUTTON_PRIMARY = 1
        return self._send_control(self._control_helper.inject_scroll_event(position, v_scroll, h_scroll, button))
    
    def SetClipboard(self, text: str, paste: bool, sequence: Optional[int] = None) -> bool:
        if sequence is None:
            sequence = self._random.randint(0, 0x7FFFFFFFFFFFFFFF) # Giả định long là 64-bit
        return self._send_control(self._control_helper.set_clipboard(text, paste, sequence))

    def GetClipboard(self, copy_key: CopyKey) -> bool:
        return self._send_control(self._control_helper.get_clipboard(copy_key))

    def SetScreenPowerMode(self, power_mode: ScrcpyScreenPowerMode) -> bool:
        return self._send_control(self._control_helper.set_screen_power_mode(power_mode))

    def BackOrScreenOn(self, key_event_action: AndroidKeyEventAction) -> bool:
        return self._send_control(self._control_helper.back_or_screen_on(key_event_action))

    def ExpandNotificationPanel(self) -> bool:
        return self._send_control(self._control_helper.expand_notification_panel())

    def ExpandSettingsPanel(self) -> bool:
        return self._send_control(self._control_helper.expand_settings_panel())

    def CollapsePanel(self) -> bool:
        return self._send_control(self._control_helper.collapse_panel())
        
    def RotateDevice(self) -> bool:
        return self._send_control(self._control_helper.rotate_device())

    def OpenHardKeyboardSetting(self) -> bool:
        return self._send_control(self._control_helper.open_hard_keyboard_setting())




    def _send_control(self, command: bytes) -> bool:
        return self.Scrcpy.SendControl(command)

    # --- Native Event Handlers (delegate giờ trả bool về native) ---

    def _native_on_clipboard_received(self, int_ptr: int, length: int) -> bool:
        clipboard_text = ""
        if length > 0 and int_ptr:
            try:
                clipboard_bytes = string_at(int_ptr, length)
                clipboard_text = clipboard_bytes.decode('utf-8', errors='replace')
            except Exception:
                clipboard_text = ""

        # Cập nhật LastClipboard ngay (đồng bộ) để property phản ánh đúng
        try:
            self._scrcpy._set_last_clipboard(clipboard_text)
        except Exception:
            pass

        # Fire event ở thread riêng để không hold native thread
        def process_clipboard():
            self._scrcpy.OnClipboardReceived.Fire(self._scrcpy, clipboard_text)
        threading.Thread(target=process_clipboard, daemon=True).start()
        return True

    def _native_clipboard_acknowledgement_received(self, sequence: int) -> bool:
        # sequence là UINT64 từ native; hiện chưa expose event public.
        return True