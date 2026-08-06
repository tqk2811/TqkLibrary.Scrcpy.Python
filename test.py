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

JAR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "TqkLibraryScrcpyPython", "scrcpy-server-v4.0.jar")
DEVICE_ID = "a29bc285"


async def main():
    scrcpyConfig = ScrcpyConfig()

    # tuỳ chọn giải mã/render phía PC giờ nằm trong ClientConfig (breaking change so với 2.4)
    scrcpyConfig.ClientConfig.Filter = D3D11Filter.D3D11_FILTER_MIN_MAG_LINEAR_MIP_POINT
    scrcpyConfig.ClientConfig.HwType = FFmpegAVHWDeviceType.AV_HWDEVICE_TYPE_D3D11VA
    scrcpyConfig.ClientConfig.IsUseD3D11ForConvert = True
    scrcpyConfig.ClientConfig.IsUseD3D11ForUiRender = True  # bắt buộc khi IsUseD3D11ForConvert=True (DLL không validate, sẽ crash nếu thiếu)

    # adb, jar, timeout kết nối giờ nằm trong DeployConfig (breaking change so với 2.4)
    scrcpyConfig.DeployConfig.AdbPath = "adb.exe"  # dùng adb trong PATH
    scrcpyConfig.DeployConfig.ScrcpyServerPath = JAR_PATH
    scrcpyConfig.DeployConfig.ConnectionTimeout = 10000
    # Đặt False để bỏ push mỗi lần Connect (phải tự gọi scrcpy.PushServer() một lần trước đó)
    scrcpyConfig.DeployConfig.ForcePush = True

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
    # scrcpy 3.0 bỏ lock_video_orientation, thay bằng capture_orientation
    scrcpyConfig.ServerConfig.VideoConfig.CaptureOrientation = CaptureOrientations.Orient0
    scrcpyConfig.ServerConfig.VideoConfig.CaptureOrientationLock = CaptureOrientationLock.LockedValue
    scrcpyConfig.ServerConfig.SCID = random.randint(INT32_MIN, INT32_MAX)

    print(f"server args: {scrcpyConfig}")

    scrcpy = Scrcpy(DEVICE_ID)
    scrcpy.OnClipboardReceived.Register(on_clipboard_received)
    scrcpy.OnDisconnect.Register(on_disconnect)
    isSuccess: bool = scrcpy.Connect(scrcpyConfig)
    print(f"Connected: {isSuccess}, DeviceName: {scrcpy.DeviceName}")

    folder_path = Path("TestScreenShot")
    if folder_path.exists():
        shutil.rmtree(folder_path)
    folder_path.mkdir(parents=True, exist_ok=False)

    screenSize = scrcpy.ScreenSize
    print(f"ScreenSize: {screenSize.Width}x{screenSize.Height}")

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
        # scrcpy 3.3+ : khoảng scroll là [-16, 16] thay vì [-1, 1]
        # isControlSuccess = scrcpy.Control.InjectScrollEvent(
        #         position = Rectangle(screenSize.Width/2,screenSize.Height/2,screenSize.Width,screenSize.Height),
        #         v_scroll = -1.0, #cuộn xuống
        #         h_scroll = 0.0,
        #         button = AndroidMotionEventButton.BUTTON_NONE
        #     )
        # isControlSuccess = scrcpy.Control.SetClipboard("kiểm tra clipboard", True)
        # isControlSuccess = scrcpy.Control.GetClipboard(copy_key=CopyKey.Copy)
        # scrcpy 3.0 thay SetScreenPowerMode bằng SetDisplayPower(bool)
        # isControlSuccess = scrcpy.Control.SetDisplayPower(False)
        # isControlSuccess = scrcpy.Control.SetDisplayPower(True)
        # isControlSuccess = scrcpy.Control.BackOrScreenOn(AndroidKeyEventAction.ACTION_DOWN)
        # isControlSuccess = scrcpy.Control.ExpandNotificationPanel()
        # isControlSuccess = scrcpy.Control.ExpandSettingsPanel()
        # isControlSuccess = scrcpy.Control.CollapsePanel()
        # isControlSuccess = scrcpy.Control.RotateDevice()
        # isControlSuccess = scrcpy.Control.OpenHardKeyboardSetting()
        # --- lệnh mới của scrcpy 3.0 / 4.0 ---
        # isControlSuccess = scrcpy.Control.StartApp("com.android.settings")
        # isControlSuccess = scrcpy.Control.StartApp("+com.android.settings")  # force-stop trước khi mở
        # isControlSuccess = scrcpy.Control.ResetVideo()
        # chỉ có nghĩa khi VideoSource = Camera:
        # isControlSuccess = scrcpy.Control.CameraSetTorch(True)
        # isControlSuccess = scrcpy.Control.CameraZoomIn()
        # isControlSuccess = scrcpy.Control.CameraZoomOut()
        # chỉ dùng được với display ảo flex (NewDisplay + FlexDisplay=True):
        # isControlSuccess = scrcpy.Control.ResizeDisplay(1280, 720)
        print(f"Send control: {isControlSuccess}")

        bgr_image = scrcpy.GetScreenShot(SwsFlag.SWS_SINC)
        cv2.imwrite(f"TestScreenShot\\Test_{index:04d}.png", bgr_image)
        index += 1


def test_list_support():
    """Hỏi thiết bị xem hỗ trợ encoder/display/camera/app nào. Không cần Connect()."""
    query = ListSupportQuery()
    query.DeployConfig.AdbPath = "adb.exe"
    query.DeployConfig.ScrcpyServerPath = JAR_PATH
    query.ListEncoders = True
    query.ListDisplays = True
    query.ListCameras = True
    query.ListApps = True

    scrcpy = Scrcpy(DEVICE_ID)
    try:
        result = scrcpy.ListSupport(query)
        print("--- Video encoders ---"); pprint(result.Videos)
        print("--- Audio encoders ---"); pprint(result.Audios)
        print("--- Displays ---");       pprint(result.Displays)
        print("--- Cameras ---");        pprint(result.CameraInfos)
        print("--- Apps ---");           pprint(result.Apps)
    finally:
        scrcpy.Dispose()


def on_clipboard_received(scrcpy: IScrcpy, text: str) -> None:
    print(f"Đã nhận clipboard: {text}")


def on_disconnect(scrcpy: IScrcpy, source: ScrcpyDisconnectSource) -> None:
    print(f"Disconnected: source={source.name}")


if __name__ == "__main__":
    # py test.py       -> mirror + chụp màn hình
    # py test.py list  -> chỉ query danh sách hỗ trợ
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        test_list_support()
    else:
        asyncio.run(main())
