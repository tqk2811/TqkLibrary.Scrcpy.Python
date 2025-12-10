import struct
import io
import random
import math
from typing import List, Union, Callable, Any, Tuple
from collections import namedtuple
from ..Enums import * # Giả sử các enum đã được import ở đây
from ..Structs import(
    Rectangle, # Giả sử Rectangle có các thuộc tính x, y, width, height
    Size,
)

class InvalidRangeException(Exception):
    pass

class ScrcpyControlHelper:
    """
    Tương đương với ScrcpyControlHelper.cs
    Giúp tạo các gói lệnh điều khiển nhị phân scrcpy.
    """

    # --- Internal Helper for Message Packing ---

    @staticmethod
    def _write_control_message(type: ScrcpyControlType, *payload_parts: Tuple[str, Any]) -> bytes:
        """
        Hàm chung để đóng gói thông báo điều khiển.
        payload_parts: Tuple của (format_char, value)
        Format chars (Big-Endian): B (uint8), I (uint32), q (int64), H (uint16), h (int16), ? (bool), s (bytes)
        Lưu ý: Các enum được truyền vào phải sử dụng thuộc tính .value để lấy giá trị số nguyên cơ bản.
        """
        with io.BytesIO() as stream:
            # Viết loại thông báo (1 byte, uint8)
            stream.write(struct.pack('>B', type.value))
            
            for fmt, value in payload_parts:
                if fmt == 's':
                    stream.write(value) 
                elif fmt == 'Rectangle':
                    stream.write(struct.pack('>i', int(value.X))) 
                    stream.write(struct.pack('>i', int(value.Y)))
                    stream.write(struct.pack('>H', int(value.Width))) 
                    stream.write(struct.pack('>H', int(value.Height)))
                else:
                    # Đóng gói giá trị số
                    stream.write(struct.pack('>' + fmt, value))
            return stream.getvalue()

    @staticmethod
    def _create_empty(type: ScrcpyControlType) -> bytes:
        """Tạo gói lệnh chỉ chứa loại (type)"""
        return ScrcpyControlHelper._write_control_message(type)

    # --- Fixed-Point Helpers (Giữ nguyên) ---

    @staticmethod
    def to_unsigned_fixed_point_16(f: float) -> int:
        """
        Convert a float between 0 and 1 to an unsigned 16-bit fixed-point value (0.16)
        """
        if not 0.0 <= f <= 1.0:
            # Đây là logic bảo vệ của Python, nhưng giữ lại check của C#
            pass 
        
        # 0x1p16f là 2^16 = 65536.0
        u = int(f * 65536.0)
        return min(u, 0xFFFF)

    @staticmethod
    def to_signed_fixed_point_16(f: float) -> int:
        """
        Convert a float between -1 and 1 to a signed 16-bit fixed-point value (1.15)
        """
        if not -1.0 <= f <= 1.0:
            raise InvalidRangeException("Float must be in range [-1.0, 1.0]")

        # 0x1p15f là 2^15 = 32768.0
        i = int(f * 32768.0)
        
        # Giới hạn giá trị
        i = min(i, 0x7FFF) # Int16 max: 32767
        i = max(i, -32768) # Int16 min: -32768
        return i

    # --- Command Encoders (Đã sửa) ---

    @staticmethod
    def inject_keycode(
            action: AndroidKeyEventAction,
            keycode: AndroidKeyCode,
            repeat: int = 1,
            meta_state: AndroidKeyEventMeta = 0x8000) -> bytes: # META_META_ON (0x8000)
        """TYPE_INJECT_KEYCODE"""
        # C#: (type, action, keycode, repeat, metaState)
        # Loại: B (byte), action: B (byte), keycode: I (uint), repeat: I (uint), metaState: I (uint)
        # action (AndroidKeyEventAction): byte -> B
        # keycode (AndroidKeyCode): uint -> I
        # repeat (uint): uint -> I
        # meta_state (AndroidKeyEventMeta): uint -> I
        return ScrcpyControlHelper._write_control_message(
            ScrcpyControlType.TYPE_INJECT_KEYCODE,
            ('B', action.value),
            ('I', keycode.value),
            ('I', repeat), # repeat là uint/int32 trong scrcpy, dùng I
            ('I', meta_state.value)
        )

    @staticmethod
    def inject_text(text: str) -> bytes:
        """TYPE_INJECT_TEXT"""
        if not text:
            raise ValueError("Text cannot be empty or None")

        utf8_text = text.encode('utf-8')
        # C#: (type, (UInt32)utf8_text.Length, utf8_text)
        # length: UInt32 -> I, text: bytes -> s
        return ScrcpyControlHelper._write_control_message(
            ScrcpyControlType.TYPE_INJECT_TEXT,
            ('I', len(utf8_text)),
            ('s', utf8_text)
        )

    @staticmethod
    def inject_touch_event(
            action: AndroidMotionEventAction,
            pointer_id: int,
            position: Rectangle,
            pressure: float,
            buttons: AndroidMotionEventButton,
            action_button: AndroidMotionEventButton) -> bytes:
        """TYPE_INJECT_TOUCH_EVENT"""
        if pressure not in (1.0, 0.0):
            raise InvalidRangeException("pressure must be 0.0f or 1.0f")

        # C#: (type, action, pointerId, position, ToUnsignedFixedPoint16(pressure), actionButton, buttons)
        # action (AndroidMotionEventAction): byte -> B
        # pointer_id (long): int64 -> q
        # position: Rectangle -> Rectangle (4 x H)
        # pressure (ushort): uint16 -> H
        # action_button (AndroidMotionEventButton): int/enum 4 bytes -> I
        # buttons (AndroidMotionEventButton): int/enum 4 bytes -> I
        return ScrcpyControlHelper._write_control_message(
            ScrcpyControlType.TYPE_INJECT_TOUCH_EVENT,
            ('B', action.value),
            ('q', pointer_id),
            ('Rectangle', position),
            ('H', ScrcpyControlHelper.to_unsigned_fixed_point_16(pressure)),
            ('I', action_button.value), 
            ('I', buttons.value)
        )

    @staticmethod
    def inject_scroll_event(
        position: Rectangle,
        v_scroll: float,
        h_scroll: float,
        button: AndroidMotionEventButton) -> bytes:
        """TYPE_INJECT_SCROLL_EVENT"""
        if not (-1.0 <= v_scroll <= 1.0):
            raise InvalidRangeException("vScroll must be in range -1.0f <= vScroll <= 1.0f")
        if not (-1.0 <= h_scroll <= 1.0):
            raise InvalidRangeException("hScroll must be in range -1.0f <= hScroll <= 1.0f")

        # C#: (type, position, ToSignedFixedPoint16(hScroll), ToSignedFixedPoint16(vScroll), button)
        # position: Rectangle -> Rectangle (4 x H)
        # hScroll (short): int16 -> h
        # vScroll (short): int16 -> h
        # button (AndroidMotionEventButton): int/enum (giả định 4 bytes) -> I
        return ScrcpyControlHelper._write_control_message(
            ScrcpyControlType.TYPE_INJECT_SCROLL_EVENT,
            ('Rectangle', position),
            ('h', ScrcpyControlHelper.to_signed_fixed_point_16(h_scroll)),
            ('h', ScrcpyControlHelper.to_signed_fixed_point_16(v_scroll)),
            ('I', button.value)
        )

    @staticmethod
    def set_clipboard(text: str, paste: bool, sequence: int) -> bytes:
        """TYPE_SET_CLIPBOARD"""
        if not text:
            raise ValueError("Text cannot be empty or None")

        utf8_text = text.encode('utf-8')
        # C#: (type, sequence, paste, (UInt32)utf8_text.Length, utf8_text)
        # sequence (long): int64 -> q
        # paste (bool): bool -> ?
        # length (UInt32): uint32 -> I
        # text: bytes -> s
        return ScrcpyControlHelper._write_control_message(
            ScrcpyControlType.TYPE_SET_CLIPBOARD,
            ('q', sequence),
            ('?', paste),
            ('I', len(utf8_text)),
            ('s', utf8_text)
        )
    
    @staticmethod
    def get_clipboard(copy_key: CopyKey) -> bytes:
        """TYPE_GET_CLIPBOARD"""
        # C#: (type, copyKey)
        # copy_key (CopyKey): byte -> B
        return ScrcpyControlHelper._write_control_message(
            ScrcpyControlType.TYPE_GET_CLIPBOARD,
            ('B', copy_key.value)
        )

    @staticmethod
    def set_screen_power_mode(power_mode: ScrcpyScreenPowerMode) -> bytes:
        """TYPE_SET_SCREEN_POWER_MODE"""
        # C#: (type, powerMode)
        # power_mode (ScrcpyScreenPowerMode): byte -> B
        return ScrcpyControlHelper._write_control_message(
            ScrcpyControlType.TYPE_SET_SCREEN_POWER_MODE,
            ('B', power_mode.value)
        )

    @staticmethod
    def back_or_screen_on(key_event_action: AndroidKeyEventAction) -> bytes:
        """TYPE_BACK_OR_SCREEN_ON"""
        # C#: (type, KeyEventAction)
        # key_event_action (AndroidKeyEventAction): byte -> B
        return ScrcpyControlHelper._write_control_message(
            ScrcpyControlType.TYPE_BACK_OR_SCREEN_ON,
            ('B', key_event_action.value)
        )

    @staticmethod
    def expand_notification_panel() -> bytes:
        """TYPE_EXPAND_NOTIFICATION_PANEL"""
        return ScrcpyControlHelper._create_empty(ScrcpyControlType.TYPE_EXPAND_NOTIFICATION_PANEL)

    @staticmethod
    def expand_settings_panel() -> bytes:
        """TYPE_EXPAND_SETTINGS_PANEL"""
        return ScrcpyControlHelper._create_empty(ScrcpyControlType.TYPE_EXPAND_SETTINGS_PANEL)

    @staticmethod
    def collapse_panel() -> bytes:
        """TYPE_COLLAPSE_PANELS"""
        return ScrcpyControlHelper._create_empty(ScrcpyControlType.TYPE_COLLAPSE_PANELS)

    @staticmethod
    def rotate_device() -> bytes:
        """TYPE_ROTATE_DEVICE"""
        return ScrcpyControlHelper._create_empty(ScrcpyControlType.TYPE_ROTATE_DEVICE)
    
    @staticmethod
    def open_hard_keyboard_setting() -> bytes:
        """OPEN_HARD_KEYBOARD_SETTINGS"""
        return ScrcpyControlHelper._create_empty(ScrcpyControlType.OPEN_HARD_KEYBOARD_SETTINGS)

    # --- UHID Commands ---

    @staticmethod
    def uhdi_create(id: int, data: bytes) -> bytes:
        """TYPE_UHID_CREATE"""
        # C#: (type, id, (UInt16)data.Length, data)
        # id (UInt16): uint16 -> H
        # length (UInt16): uint16 -> H
        # data: bytes -> s
        return ScrcpyControlHelper._write_control_message(
            ScrcpyControlType.TYPE_UHID_CREATE,
            ('H', id),
            ('H', len(data)),
            ('s', data)
        )

    @staticmethod
    def uhdi_input(id: int, data: bytes) -> bytes:
        """TYPE_UHID_INPUT"""
        # C#: (type, id, (UInt16)data.Length, data)
        # id (UInt16): uint16 -> H
        # length (UInt16): uint16 -> H
        # data: bytes -> s
        return ScrcpyControlHelper._write_control_message(
            ScrcpyControlType.TYPE_UHID_INPUT,
            ('H', id),
            ('H', len(data)),
            ('s', data)
        )