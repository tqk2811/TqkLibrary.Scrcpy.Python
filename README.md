# TqkLibrary.Scrcpy.Python

Wrapper Python cho scrcpy, port 1-1 từ thư viện C# [TqkLibrary.Scrcpy](https://github.com/tqk2811/TqkLibrary.Scrcpy)
(branch `4.0`). Phần decode/render chạy trong `TqkLibrary.ScrcpyNative.dll`; phần adb, socket,
tiến trình server và sinh tham số nằm ở tầng Python.

## Yêu cầu

- Windows x64 (DLL native chỉ build cho Windows)
- Python 3.8+, `pip install -r requirements.txt` (`opencv-python`, `numpy`)
- `adb` trong PATH hoặc chỉ định qua `DeployConfig.AdbPath`
- Thiết bị Android bật USB debugging

Package đã kèm sẵn `scrcpy-server-v4.0.jar` và bộ DLL FFmpeg trong `TqkLibraryScrcpyPython/x64/`.

## Dùng nhanh

```python
import os
from TqkLibraryScrcpyPython import *

config = ScrcpyConfig()
config.DeployConfig.AdbPath = "adb.exe"
config.DeployConfig.ScrcpyServerPath = os.path.join(
    os.path.dirname(__file__), "TqkLibraryScrcpyPython", "scrcpy-server-v4.0.jar")

scrcpy = Scrcpy("<device-id>")
if scrcpy.Connect(config):
    print(scrcpy.DeviceName, scrcpy.ScreenSize.Width, "x", scrcpy.ScreenSize.Height)
    bgr = scrcpy.GetScreenShot(SwsFlag.SWS_FAST_BILINEAR)   # numpy ndarray BGR
    scrcpy.Control.StartApp("com.android.settings")
scrcpy.Dispose()
```

Xem thêm [test.py](test.py) (`py test.py` để mirror, `py test.py list` để query danh sách hỗ trợ).

### Bỏ push jar mỗi lần connect

Jar nằm lại trên thiết bị giữa các lần kết nối nên push lại chỉ tốn thời gian:

```python
scrcpy.PushServer(config.DeployConfig)      # gọi một lần
config.DeployConfig.ForcePush = False       # các lần Connect sau bỏ qua push
```

### Query hỗ trợ của thiết bị

```python
query = ListSupportQuery()
query.DeployConfig = config.DeployConfig   # dùng chung để không đẩy jar ra 2 path khác nhau
query.ListEncoders = query.ListDisplays = query.ListApps = True
result = scrcpy.ListSupport(query)
print(result.Videos, result.Displays, result.Apps)
```

## Breaking change khi lên 4.0 (từ bản 2.4)

Bản này **không giữ alias tương thích ngược** — bám sát API của C# branch `4.0`.

| 2.4 | 4.0 | Ghi chú |
|---|---|---|
| `ScrcpyConfig.AdbPath` | `ScrcpyConfig.DeployConfig.AdbPath` | |
| `ScrcpyConfig.ScrcpyServerPath` | `ScrcpyConfig.DeployConfig.ScrcpyServerPath` | |
| `ScrcpyConfig.ConnectionTimeout` | `ScrcpyConfig.DeployConfig.ConnectionTimeout` | |
| `ScrcpyConfig.HwType` / `Filter` / `IsUseD3D11ForUiRender` / `IsUseD3D11ForConvert` / `IsForceUiGpuFlush` | `ScrcpyConfig.ClientConfig.*` | gom tuỳ chọn giải mã/render phía PC |
| `ScrcpyConfig.GpuThreadX` / `GpuThreadY` | *(bỏ)* | struct native đã bỏ 2 field này |
| `Control.SetScreenPowerMode(mode)` | `Control.SetDisplayPower(on: bool)` | |
| `ScrcpyScreenPowerMode` | *(bỏ)* | |
| `VideoConfig.Orientation` + `Orientations` | `VideoConfig.CaptureOrientation` + `CaptureOrientationLock` | scrcpy 3.0 bỏ `lock_video_orientation` |
| `VideoConfig.MaxFps: int` | `VideoConfig.MaxFps: float` | |
| `InjectScrollEvent` nhận `[-1, 1]` | nhận `[-16, 16]` | scrcpy 3.3+ |
| `InjectText` chỉ nhận ASCII | nhận UTF-8 | |
| `uhdi_create(id, data)` | thêm `name`, `vendor_id`, `product_id` | scrcpy 3.1+ |

Số hiệu `ScrcpyControlType` cũng đổi: `TYPE_UHID_DESTROY` chèn vào `14`, đẩy
`OPEN_HARD_KEYBOARD_SETTINGS` sang `15`. Server **không validate** — client 2.4 nói chuyện với
server 4.0 sẽ thực thi nhầm lệnh chứ không báo lỗi. Đừng trộn lẫn phiên bản.

### Bổ sung mới

- Config: `ScreenOffTimeout`, `NewDisplay`, `VdSystemDecorations`, `VdDestroyContent`,
  `DisplayImePolicy`, `KeepActive`, `Angle`, `MinSizeAlignment`, `FlexDisplay`,
  `AudioSource`, `AudioDup`, `CameraZoom`, `CameraTorch`
- Control: `StartApp`, `ResetVideo`, `CameraSetTorch`, `CameraZoomIn`, `CameraZoomOut`,
  `ResizeDisplay`, `UhidDestroy`
- `Scrcpy.PushServer()`, `Scrcpy.ListSupport()`

## Tài liệu

- [docs/Upgrade-4.0-Plan-vi.md](docs/Upgrade-4.0-Plan-vi.md) — kế hoạch & ghi chú nâng cấp 2.4 → 4.0
- [docs/Glossary-vi.md](docs/Glossary-vi.md) — thuật ngữ

## Build lại DLL native

DLL đi kèm build từ branch `4.0` của repo C# (`TqkLibrary.ScrcpyNative.vcxproj`, cấu hình
`x64 / Release`). Nếu build lại, nhớ kiểm tra `ctypes.sizeof(ScrcpyNativeConfig) == 20` —
struct lệch offset không gây lỗi lúc chạy, chỉ khiến native đọc giá trị rác.
