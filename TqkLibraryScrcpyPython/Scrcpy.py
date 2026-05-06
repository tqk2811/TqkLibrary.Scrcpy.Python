import os
import re
import socket
import subprocess
import threading
from typing import Optional, List
from ctypes import (
    c_void_p, c_int, c_int32, c_uint32, c_ubyte, c_bool, c_longlong,
    POINTER, byref,
)

from .NativeWrapper import (
    ScrcpyAlloc, ScrcpyFree, ScrcpyConnect, ScrcpyStop,
    IsHaveScrcpyInstance,
    ScrcpyGetScreenSize,
    ScrcpyControlCommand,
    ScrcpyGetScreenShot,
    ScrcpyReadAudioRaw,
    RegisterDisconnectEvent, NativeOnDisconnectDelegate,
    RegisterClipboardEvent, NativeOnClipboardReceivedDelegate,
    RegisterClipboardAcknowledgementEvent, NativeOnClipboardAcknowledgementDelegate,
    RegisterUhdiOutputEvent, NativeUhdiOutputDelegate,
)
from .Configs import ScrcpyConfig, ScrcpyNativeConfig
from .Controls import ScrcpyControl
from .Structs import Size
from .Interfaces import IScrcpy
from .Events import DisconnectEvent, ClipboardEvent
from .Enums import SwsFlag, ScrcpyDisconnectSource, AVSampleFormat

import numpy as np

INVALID_SOCKET = c_void_p(-1)


def _socket_handle(s: Optional[socket.socket]) -> c_void_p:
    """Lấy SOCKET handle của Python socket để truyền cho native (Windows: SOCKET = UINT_PTR)."""
    if s is None:
        return INVALID_SOCKET
    return c_void_p(s.fileno())


class Scrcpy(IScrcpy):
    def __init__(self, deviceId: str):
        if not deviceId or not deviceId.strip():
            raise ValueError("deviceId cannot be empty or whitespace")

        self._deviceId: str = deviceId
        self._deviceName: str = ""
        self._adbPath: str = "adb.exe"
        self._lastClipboard: str = ""

        self._disconnectEvent = DisconnectEvent()
        self._clipboardEvent = ClipboardEvent()

        self._handle = ScrcpyAlloc()
        if not self._handle:
            raise RuntimeError("ScrcpyAlloc failed")

        self._control: ScrcpyControl = ScrcpyControl(self)

        # Native callbacks — phải giữ ref trên instance để GC không thu hồi thunk
        self._native_on_disconnect_delegate = NativeOnDisconnectDelegate(self._on_disconnect_callback)
        if not RegisterDisconnectEvent(self._handle, self._native_on_disconnect_delegate):
            raise RuntimeError("Failed to register disconnect event.")

        self._uhdi_output_delegate = NativeUhdiOutputDelegate(self._uhdi_output_callback)
        if not RegisterUhdiOutputEvent(self._handle, self._uhdi_output_delegate):
            raise RuntimeError("Failed to register UHDI output event.")

        self._countdown_event = threading.Semaphore(1)
        self._is_disposed = False
        self._serverProcess: Optional[subprocess.Popen] = None
        self._activeSockets: Optional[List[Optional[socket.socket]]] = None
        self._screen_size_cache: Optional[Size] = None

    # --- Properties ---

    @property
    def DeviceId(self) -> str:
        return self._deviceId

    @property
    def DeviceName(self) -> str:
        return self._deviceName

    @property
    def IsConnected(self) -> bool:
        with self._countdown_event:
            return IsHaveScrcpyInstance(self._handle)

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

    # --- Connect / Stop ---

    def Connect(self, config: Optional[ScrcpyConfig] = None) -> bool:
        if self._is_disposed:
            return False
        if config is None:
            config = ScrcpyConfig()

        self._adbPath = config.AdbPath
        self._screen_size_cache = None
        native_config = config.NativeConfig()

        scid = config.ServerConfig.SCID if config.ServerConfig else -1
        scid_prefix = "localabstract:scrcpy"
        if scid != -1:
            scid_prefix += f"_{(scid & 0x7FFFFFFF):x}"

        is_video = bool(native_config.IsVideo)
        is_audio = bool(native_config.IsAudio)
        is_control = bool(native_config.IsControl)
        backlog = (1 if is_video else 0) + (1 if is_audio else 0) + (1 if is_control else 0)

        # Listener trên loopback, port 0 → OS tự cấp port không trùng
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            listener.bind(("127.0.0.1", 0))
            listener.listen(backlog)
        except Exception:
            listener.close()
            return False
        port = listener.getsockname()[1]

        # Setup ADB tunnel + push server jar
        # Bỏ qua lỗi của reverse --remove (rule có thể chưa tồn tại)
        self._run_adb_sync(config.AdbPath, ["-s", self._deviceId, "reverse", "--remove", scid_prefix])
        if self._run_adb_sync(
            config.AdbPath,
            ["-s", self._deviceId, "push", config.ScrcpyServerPath, "/sdcard/scrcpy-server-tqk.jar"],
        ) != 0:
            listener.close()
            return False
        if self._run_adb_sync(
            config.AdbPath,
            ["-s", self._deviceId, "reverse", scid_prefix, f"tcp:{port}"],
        ) != 0:
            listener.close()
            return False

        # Spawn scrcpy server qua adb shell
        cfg_str = str(config).strip()
        cfg_args = cfg_str.split() if cfg_str else []
        server_cmd = [
            config.AdbPath, "-s", self._deviceId, "shell",
            "CLASSPATH=/sdcard/scrcpy-server-tqk.jar",
            "app_process", "/", "com.genymobile.scrcpy.Server",
        ] + cfg_args
        creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            server_process = subprocess.Popen(
                server_cmd,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creation_flags,
            )
        except Exception:
            listener.close()
            return False

        # Accept video → audio → control theo đúng thứ tự server connect
        timeout_sec = max(1, native_config.ConnectionTimeout) / 1000.0
        listener.settimeout(timeout_sec)
        video_sock: Optional[socket.socket] = None
        audio_sock: Optional[socket.socket] = None
        control_sock: Optional[socket.socket] = None
        first_sock: Optional[socket.socket] = None

        def cleanup_failed():
            for s in (video_sock, audio_sock, control_sock):
                if s is not None:
                    try: s.close()
                    except Exception: pass
            try: server_process.kill()
            except Exception: pass
            try: server_process.wait(timeout=2)
            except Exception: pass
            listener.close()

        try:
            if is_video:
                video_sock, _ = listener.accept()
                first_sock = first_sock or video_sock
            if is_audio:
                audio_sock, _ = listener.accept()
                first_sock = first_sock or audio_sock
            if is_control:
                control_sock, _ = listener.accept()
                first_sock = first_sock or control_sock
        except Exception:
            cleanup_failed()
            return False
        finally:
            # listener không cần nữa sau khi accept đủ
            try: listener.close()
            except Exception: pass

        # Đọc 64-byte device name từ first socket
        if first_sock is not None:
            try:
                first_sock.settimeout(timeout_sec)
                buf = bytearray()
                while len(buf) < 64:
                    chunk = first_sock.recv(64 - len(buf))
                    if not chunk:
                        raise IOError("Connection closed while reading device name")
                    buf.extend(chunk)
                first_sock.settimeout(None)
                null_idx = buf.find(b"\x00")
                end = null_idx if null_idx >= 0 else len(buf)
                self._deviceName = buf[:end].decode("ascii", errors="replace")
            except Exception:
                cleanup_failed()
                return False

        # Pass socket fd vào native và thực hiện ScrcpyConnect
        try:
            with self._countdown_event:
                connected = ScrcpyConnect(
                    self._handle,
                    POINTER(ScrcpyNativeConfig)(native_config),
                    _socket_handle(video_sock),
                    _socket_handle(audio_sock),
                    _socket_handle(control_sock),
                )
        except Exception:
            cleanup_failed()
            return False

        if connected:
            self._serverProcess = server_process
            self._activeSockets = [video_sock, audio_sock, control_sock]
        else:
            cleanup_failed()
        return bool(connected)

    def Stop(self) -> None:
        if self._is_disposed:
            return
        if not self._countdown_event.acquire(blocking=False):
            return
        try:
            ScrcpyStop(self._handle)
            sockets = self._activeSockets
            self._activeSockets = None
            if sockets:
                for s in sockets:
                    if s is not None:
                        try: s.close()
                        except Exception: pass
            proc = self._serverProcess
            self._serverProcess = None
            if proc is not None:
                try: proc.kill()
                except Exception: pass
                try: proc.wait(timeout=2)
                except Exception: pass
        finally:
            self._countdown_event.release()

    # --- Screen size & screenshot ---

    def _get_screen_size(self) -> Size:
        w = c_int32(0)
        h = c_int32(0)
        with self._countdown_event:
            ScrcpyGetScreenSize(self._handle, byref(w), byref(h))
        if w.value == -1 or h.value == -1:
            return self._screen_size_cache or Size(0, 0)
        return Size(w.value, h.value)

    def GetScreenShot(self, swsFlag: Optional[SwsFlag] = None) -> Optional[np.ndarray]:
        if self._is_disposed:
            return None

        size = self._get_screen_size()
        if size.Width <= 0 or size.Height <= 0:
            return None

        width = size.Width
        fix_width = width if width % 16 == 0 else width + 16 - (width % 16)
        fix_size = Size(fix_width, size.Height)
        buffer_size = fix_size.Width * fix_size.Height * 4
        image_buffer = (c_ubyte * buffer_size)()

        if swsFlag is None:
            swsFlag = SwsFlag.SWS_FAST_BILINEAR

        with self._countdown_event:
            ok = ScrcpyGetScreenShot(
                self._handle,
                image_buffer,
                buffer_size,
                size.Width,
                size.Height,
                fix_size.Width * 4,
                int(swsFlag.value),
            )

        if not ok:
            return None

        img = np.frombuffer(image_buffer, dtype=np.uint8).reshape(fix_size.Height, fix_size.Width, 4)
        if size.Width != fix_size.Width:
            img = img[: size.Height, : size.Width, :]
        return img[:, :, :3]  # BGR

    def ReadAudioRaw(
        self,
        buffer: bytearray,
        out_nb_channels: int,
        out_sample_rate: int,
        out_sample_fmt: AVSampleFormat,
        last_pts: int = -1,
        wait_frame_time_ms: int = 0,
    ) -> Optional[tuple]:
        """Đọc audio frame đã resample. Trả (current_pts, bytes_written) hoặc None nếu lỗi.
        current_pts = -1 nếu không có frame mới."""
        if self._is_disposed:
            return None
        size = len(buffer)
        if size <= 0:
            return None
        c_buffer = (c_ubyte * size).from_buffer(buffer)
        out_bytes = c_int32(0)
        with self._countdown_event:
            pts = ScrcpyReadAudioRaw(
                self._handle,
                c_buffer,
                size,
                int(out_nb_channels),
                int(out_sample_rate),
                int(out_sample_fmt.value),
                int(last_pts),
                int(wait_frame_time_ms),
                byref(out_bytes),
            )
        return (pts, out_bytes.value)

    # --- Control send ---

    def SendControl(self, command: bytes) -> bool:
        if self._is_disposed or not command:
            return False
        c_command = (c_ubyte * len(command))(*command)
        with self._countdown_event:
            return bool(ScrcpyControlCommand(self._handle, c_command, len(command)))

    # --- Native register helpers (gọi từ ScrcpyControl) ---

    def _register_clipboard_event(self, method: NativeOnClipboardReceivedDelegate) -> bool:
        return RegisterClipboardEvent(self._handle, method)

    def _register_clipboard_acknowledgement_event(self, method: NativeOnClipboardAcknowledgementDelegate) -> bool:
        return RegisterClipboardAcknowledgementEvent(self._handle, method)

    def _set_last_clipboard(self, data: str) -> None:
        self._lastClipboard = data

    # --- Native callbacks ---

    def _on_disconnect_callback(self, source: int) -> bool:
        try:
            src = ScrcpyDisconnectSource(source)
        except ValueError:
            src = ScrcpyDisconnectSource.Video

        def run():
            self.Stop()
            self.OnDisconnect.Fire(self, src)

        threading.Thread(target=run, daemon=True).start()
        return True

    def _uhdi_output_callback(self, id: int, size: int, buff: int) -> bool:
        # buff là pointer thô, hiện tại không xử lý.
        return True

    # --- ADB helpers ---

    def _run_adb_sync(self, adb_path: str, args: List[str]) -> int:
        try:
            creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            return subprocess.run(
                [adb_path] + args,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creation_flags,
            ).returncode
        except Exception:
            return -1

    def RefreshScreenSizeFromAdb(self, timeout_sec: float = 5.0) -> Size:
        """Query screen size qua `adb shell wm size`. Dùng khi IsVideo=False."""
        try:
            creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
            result = subprocess.run(
                [self._adbPath, "-s", self._deviceId, "shell", "wm", "size"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                timeout=timeout_sec,
                creationflags=creation_flags,
            )
            output = result.stdout.decode("utf-8", errors="replace")
            matches = re.findall(r"(\d+)x(\d+)", output)
            if matches:
                w, h = matches[-1]
                self._screen_size_cache = Size(int(w), int(h))
                return self._screen_size_cache
        except Exception:
            pass
        return Size(0, 0)

    # --- Lifecycle ---

    def __del__(self):
        try:
            self.Dispose(False)
        except Exception:
            pass

    def Dispose(self, disposing: bool = True) -> None:
        if self._is_disposed:
            return
        self._is_disposed = True

        # Stop trước khi đóng cửa semaphore
        try:
            ScrcpyStop(self._handle)
        except Exception:
            pass
        sockets = self._activeSockets
        self._activeSockets = None
        if sockets:
            for s in sockets:
                if s is not None:
                    try: s.close()
                    except Exception: pass
        proc = self._serverProcess
        self._serverProcess = None
        if proc is not None:
            try: proc.kill()
            except Exception: pass
            try: proc.wait(timeout=2)
            except Exception: pass

        # Đợi các op trong-flight (timeout 5s) rồi free handle
        try:
            self._countdown_event.acquire(blocking=True, timeout=5)
        except Exception:
            pass

        if self._handle:
            try: ScrcpyFree(self._handle)
            except Exception: pass
            self._handle = None
