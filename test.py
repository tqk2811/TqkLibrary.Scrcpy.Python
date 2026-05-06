from TqkLibraryScrcpyPython import *
import os
import sys
import ctypes
from pprint import pprint
import cv2
import asyncio
import random
from pathlib import Path
import shutil

INT32_MIN = -2147483648
INT32_MAX = 2147483647

async def main():
    scrcpyConfig = ScrcpyConfig();
    scrcpyConfig.Filter = D3D11Filter.D3D11_FILTER_MIN_MAG_LINEAR_MIP_POINT
    scrcpyConfig.HwType = FFmpegAVHWDeviceType.AV_HWDEVICE_TYPE_D3D11VA
    scrcpyConfig.IsUseD3D11ForConvert = True
    scrcpyConfig.IsUseD3D11ForUiRender = True  # bắt buộc khi IsUseD3D11ForConvert=True (DLL không validate, sẽ crash nếu thiếu)
    scrcpyConfig.ConnectionTimeout = 10000
    scrcpyConfig.AdbPath = "adb.exe"#dùng adb trong PATH
    scrcpyConfig.ScrcpyServerPath = os.path.dirname(os.path.abspath(__file__)) + "\\TqkLibraryScrcpyPython\\scrcpy-server-v2.4.jar"
    scrcpyConfig.ServerConfig = ScrcpyServerConfig()
    scrcpyConfig.ServerConfig.IsControl = True
    scrcpyConfig.ServerConfig.VideoSource = VideoSource.Display
    scrcpyConfig.ServerConfig.AndroidConfig = AndroidConfig()
    scrcpyConfig.ServerConfig.AndroidConfig.ShowTouches = True
    scrcpyConfig.ServerConfig.AndroidConfig.StayAwake = True
    scrcpyConfig.ServerConfig.AndroidConfig.PowerOn = True
    scrcpyConfig.ServerConfig.Cleanup = False
    scrcpyConfig.ServerConfig.ClipboardAutosync = False
    scrcpyConfig.ServerConfig.VideoConfig = VideoConfig()
    scrcpyConfig.ServerConfig.VideoConfig.MaxFps = 6
    scrcpyConfig.ServerConfig.VideoConfig.Orientation = Orientations.Natural
    scrcpyConfig.ServerConfig.SCID = random.randint(INT32_MIN, INT32_MAX)
    scrcpy = Scrcpy("a29bc285")
    scrcpy.OnClipboardReceived.Register(on_clipboard_received)
    scrcpy.OnDisconnect.Register(on_disconnect)
    isSuccess: bool = scrcpy.Connect(scrcpyConfig)
    print(f"DeviceName: {scrcpy.DeviceName}")

    folder_path = Path("TestScreenShot")
    if folder_path.exists():
        shutil.rmtree(folder_path)
    folder_path.mkdir(parents=True, exist_ok=False)

    screenSize = scrcpy.ScreenSize

    index = 0
    while isSuccess:
        await asyncio.sleep(1)

        isControlSuccess: bool = False
        # isControlSuccess = scrcpy.Control.InjectText("test inject")
        # pointerId = random.randint(INT32_MIN, INT32_MAX) #hoặc ScrcpyMousePointerId.POINTER_ID_MOUSE
        # posTap = Rectangle(screenSize.Width/2,screenSize.Height/2,screenSize.Width,screenSize.Height)#giữa màn hình
        # isControlSuccess = scrcpy.Control.InjectTouchEvent(
        #         action = AndroidMotionEventAction.ACTION_DOWN,
        #         pointer_id = pointerId,
        #         position = posTap,
        #         pressure = 1.0,
        #         buttons = AndroidMotionEventButton.BUTTON_PRIMARY,
        #         action_button = AndroidMotionEventButton.BUTTON_PRIMARY
        #     )
        # await asyncio.sleep(0.1)
        # isControlSuccess = scrcpy.Control.InjectTouchEvent(
        #         action = AndroidMotionEventAction.ACTION_UP,
        #         pointer_id = pointerId,
        #         position = posTap,
        #         pressure = 1.0,
        #         buttons = AndroidMotionEventButton.BUTTON_PRIMARY,
        #         action_button = AndroidMotionEventButton.BUTTON_PRIMARY
        #     )
        # isControlSuccess = scrcpy.Control.InjectScrollEvent(
        #         position = Rectangle(screenSize.Width/2,screenSize.Height/2,screenSize.Width,screenSize.Height),
        #         v_scroll = -1.0, #cuộn xuống
        #         h_scroll = 0.0,
        #         button = AndroidMotionEventButton.BUTTON_NONE
        #     )
        # isControlSuccess = scrcpy.Control.SetClipboard("kiểm tra clipboard", True)
        # isControlSuccess = scrcpy.Control.GetClipboard(copy_key=CopyKey.Copy)
        # isControlSuccess = scrcpy.Control.SetScreenPowerMode(ScrcpyScreenPowerMode.POWER_MODE_OFF)
        # isControlSuccess = scrcpy.Control.SetScreenPowerMode(ScrcpyScreenPowerMode.POWER_MODE_NORMAL)
        # isControlSuccess = scrcpy.Control.BackOrScreenOn(AndroidKeyEventAction.ACTION_DOWN)
        # isControlSuccess = scrcpy.Control.ExpandNotificationPanel()
        # isControlSuccess = scrcpy.Control.ExpandSettingsPanel()
        # isControlSuccess = scrcpy.Control.CollapsePanel()
        # isControlSuccess = scrcpy.Control.RotateDevice()
        # isControlSuccess = scrcpy.Control.OpenHardKeyboardSetting()
        print(f"Send control: {isControlSuccess}")           

        bgr_image = scrcpy.GetScreenShot(SwsFlag.SWS_SINC)
        cv2.imwrite(f"TestScreenShot\\Test_{index:04d}.png", bgr_image)
        index += 1

def on_clipboard_received(scrcpy: IScrcpy, text: str) -> None:
    print(f"Đã nhận clipboard: {text}")

def on_disconnect(scrcpy: IScrcpy, source: ScrcpyDisconnectSource) -> None:
    print(f"Disconnected: source={source.name}")

if __name__ == "__main__":
    asyncio.run(main())