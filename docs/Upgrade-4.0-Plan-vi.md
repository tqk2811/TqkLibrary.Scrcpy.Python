# Kế hoạch nâng cấp TqkLibrary.Scrcpy.Python lên 4.0

Bám sát branch `4.0` của `D:\IT\Csharp\Libraries\TqkLibrary.Scrcpy` (mốc `4c4f6cb`).

## Tiến độ

| Bước | Trạng thái |
|---|---|
| 1 · B1 rebuild DLL native | ✅ xong — `4.0.114.0`, đã copy vào `x64/` |
| 2 · B2 sửa layout `ScrcpyNativeConfig` | ✅ xong — `sizeof == 20`, có assert chốt layout |
| 3 · B3 jar + version string | ✅ xong — `scrcpy-server-v4.0.jar`, version `"4.0"` |
| 4 · Nhóm B (`ScrcpyDeployConfig`, `PushServer`) | ✅ xong |
| 5 · Nhóm C (control protocol) | ✅ xong — đã dump hex đối chiếu |
| 6 · Nhóm D (config options) | ✅ xong |
| 7 · Nhóm E (`ListSupport`) | ✅ xong — parser test bằng output mẫu 4.0 |
| 8 · Nhóm F (test/docs) | ✅ xong — `test.py`, `README.md` |

### ✅ Đã test trên thiết bị thật — Pixel 3a (Android 12), 2026-08-06

| Hạng mục | Kết quả |
|---|---|
| `ListSupport` | 7 video encoder, 5 audio encoder, 1 display, 43 app (tên tiếng Việt decode đúng), camera 2 cái |
| `Connect` + `DeviceName` + `ScreenSize` | OK (2.6s) |
| `GetScreenShot` | OK sau khi vá (xem bên dưới) — ảnh đúng nội dung, đúng màu, không lệch stride |
| `StartApp` (opcode 16, mới) | OK — `mCurrentFocus` chuyển sang `com.android.settings` |
| `ExpandNotificationPanel` / `CollapsePanel` | OK — ảnh chụp đổi rõ rệt |
| `InjectScrollEvent` (công thức scale mới) | OK — danh sách cuộn thật |
| `SetDisplayPower` (payload đổi) | OK — SurfaceFlinger `powerMode: On(2) → Off(0) → On(2)` |
| `BackOrScreenOn` | OK — về launcher |
| `SetClipboard` + `GetClipboard` round-trip | OK, giữ nguyên chuỗi |
| `ResetVideo` (opcode 17, mới) | OK, stream không đứt |
| `IsVideo=False` (chỉ control) | OK |
| `Stop`/`Dispose` | OK — bắn `DISCONNECT Control` + `DISCONNECT Video` |

Kiểm chứng wire format bằng script Python thuần (không qua DLL) khớp đúng giả định của C++ 4.0:
session header `80 ...` MSB=1 mang width/height, gói media có cờ CONFIG ở bit 62, KEY ở bit 61.

### 🐛 Bug tìm thấy khi test — nằm ở CHÍNH thư viện C#, không phải bản port

Native `FrameConventer::Convert` (`FrameConventer.cpp:59`) tính:
```cpp
int fix_w = w + w % 16;
```
rồi từ chối nếu `linesizes[0] != lineSize`. Nhưng `Scrcpy.cs:381` (và bản Python chép theo) lại dùng:
```csharp
int width = size.Width % 16 == 0 ? size.Width : size.Width + 16 - (size.Width % 16);
```
Đây là **hai công thức khác nhau**, chỉ trùng nhau khi `w % 16 ∈ {0, 8}`. Màn hình rộng 1080
(1080 % 16 = 8) trùng ngẫu nhiên nên chạy được; Pixel 3a capture ra width **1050** (%16 = 10) ⇒
C#/Python gửi `lineSize = 1056·4`, native đòi `1060·4` ⇒ `GetScreenShot` trả false **im lặng**.

Tính ra 6/8 giá trị `w % 16` chẵn là hỏng — tức đa số độ rộng đều chụp màn hình không được.

Nguồn gốc: commit `d3337b6` (2023-04-01, *"scrcpy.GetScreenShot: fix width div 16"*) đổi tầng
managed từ `size.Width + size.Width % 16` (khớp native) sang công thức làm tròn lên — sửa đúng ý đồ
nhưng quên tầng native, nên lệch suốt 3 năm và lan sang mọi branch tách sau.

**Đã vá cả hai bên:**
- Python: [Scrcpy.py](../TqkLibraryScrcpyPython/Scrcpy.py) dùng công thức của native.
- C#: commit `d549899` *"fix(screenshot): match the native padded-width formula in GetScreenShot"*
  trên branch `2.4`, đã merge lên `2.5`→`4.0` (8 branch, không conflict). Branch `master` chưa vá.

### Lưu ý khi bàn giao

- `TqkLibraryScrcpyPython/x64/` nằm trong `.gitignore` → **DLL mới không được git theo dõi**.
  Nó chỉ tồn tại trên đĩa máy này; phân phối qua `pack.bat`. Clone mới phải build lại từ
  branch `4.0` của repo C#.
- Repo C# hiện đang ở branch `4.0` (trước đó là `3.3`), working tree sạch.
- `version.generated.h` của repo C# đã sinh lại cho `4.0.114` (file này bị gitignore).

## Quyết định đã chốt

| | |
|---|---|
| **Phạm vi** | Port cả `ListSupport` trong đợt này (Nhóm E nằm trong scope, không hoãn) |
| **Tương thích ngược** | Breaking thẳng, không giữ alias deprecated — ghi rõ trong README |
| **Branch** | Làm thẳng trên `master` (repo Python không theo convention branch-theo-version như repo C#) |

Vì làm thẳng `master` và breaking thẳng, nên **commit bước 1–3 phải nguyên khối**: giữa chừng là
`master` ở trạng thái không chạy được.

---

## 0. Hiện trạng

| | Python (repo này) | C# branch `4.0` |
|---|---|---|
| Server jar | `scrcpy-server-v2.4.jar` | `scrcpy-server-v4.0.jar` |
| Version string handshake | `"2.4"` | `"4.0"` |
| DLL native | build **2026-05-06** | source hiện tại |
| Kiến trúc | Configs / Controls / Enums / Events / Interfaces / Structs + `NativeWrapper` + `Scrcpy` | như trên + `ListSupport` / `Helpers` / `Exceptions` / `Attributes` / `Constant` |

Python là **ảnh chụp branch `2.4` tại 2026-05-06** (commit `3a2f1ce`), tức còn thiếu cả 2 commit
mới nhất của chính branch `2.4` (xem Nhóm B). Branch `4.0` có merge-base với `3.3` đúng tại
`1f009a0` — nghĩa là `4.0` đã chứa trọn vẹn `2.4` HEAD, không cần merge thêm nhánh nào khác.

Kiến trúc Python đã bám sát C# rồi (chia thư mục, tên class, tên property đều 1-1), nên toàn bộ
việc nâng cấp là **áp delta 2.4 → 4.0**, không phải viết lại.

---

## 1. Blocker — phải làm trước, không có đường vòng

### B1. Rebuild `TqkLibrary.ScrcpyNative.dll` từ branch `4.0`

scrcpy 4.0 đổi [wire format](Glossary-vi.md#L17) của video stream. Toàn bộ phần bị ảnh hưởng nằm
trong C++ ([demuxer](Glossary-vi.md#L23)), Python **không sửa được** vì chỉ đưa socket fd vào
`ScrcpyConnect`:

- `TqkLibrary.ScrcpyNative/Video.cpp` — đầu stream không còn 8 byte `width`+`height`, thay bằng
  [session header](Glossary-vi.md#L28) 12 byte.
- `TqkLibrary.ScrcpyNative/SocketWrapper.cpp` — mỗi packet có meta header 12 byte;
  `header[0] & 0x80` phân biệt session (không payload, phải skip) với media; bit cờ dịch:
  `CONFIG 1<<63 → 1<<62`, `KEY_FRAME 1<<62 → 1<<61`; `len <= 0` là invalid.

Dùng server jar 4.0 với DLL cũ ⇒ decoder đọc rác, treo hoặc màn hình đen. Không có thông báo lỗi rõ ràng.

**Cách làm:** build `TqkLibrary.ScrcpyNative.vcxproj` cấu hình `x64 / Release` từ branch `4.0`
(script `Build.ps1` của repo C# đã lo `nuget restore` + version header), rồi copy
`TqkLibrary.ScrcpyNative.dll` vào [x64/](../TqkLibraryScrcpyPython/x64/).
Các DLL FFmpeg (`avcodec-62`, `avutil-60`, …) **không cần đổi** — không có thay đổi nào phụ thuộc chúng.

### B2. Sửa `ScrcpyNativeConfig` cho khớp [ABI](Glossary-vi.md#L34) mới

DLL đang ship (2026-05-06) còn 2 field `GpuThreadX`/`GpuThreadY`; commit `7f669e3` (2026-07-01,
`refactor(video)!: remove dead compute dispatch and unused GpuThread config`) đã xoá chúng — commit
này có mặt trong **cả `2.4` lẫn `4.0`**.

Rebuild DLL mà không sửa struct phía Python ⇒ `IsForceUiGpuFlush` lệch **8 byte**, native đọc giá trị
rác. [ctypes](Glossary-vi.md#L41) không cảnh báo gì.

- [ScrcpyNativeConfig.py](../TqkLibraryScrcpyPython/Configs/ScrcpyNativeConfig.py#L33-L34) — xoá 2 field.
- [ScrcpyConfig.py:20-21](../TqkLibraryScrcpyPython/Configs/ScrcpyConfig.py#L20-L21) và
  [ScrcpyConfig.py:43-44](../TqkLibraryScrcpyPython/Configs/ScrcpyConfig.py#L43-L44),
  [ScrcpyConfig.py:55-56](../TqkLibraryScrcpyPython/Configs/ScrcpyConfig.py#L55-L56) — xoá `GpuThreadX`/`GpuThreadY`.

**Kiểm chứng:** `ctypes.sizeof(ScrcpyNativeConfig) == 20`
(6 byte bool + 2 byte [đệm](Glossary-vi.md#L46) + `ConnectionTimeout` 4 + `Filter` 4 + `IsForceUiGpuFlush` 4).
Hiện tại là 28.

Tiện thể: [ScrcpyConfig.py:22](../TqkLibraryScrcpyPython/Configs/ScrcpyConfig.py#L22) đang mặc định
`IsForceUiGpuFlush = False`, C# mặc định `true` → chỉnh lại cho khớp.

### B3. Thay server jar + version string

- Copy `scrcpy-server-v4.0.jar` từ root repo C# vào [TqkLibraryScrcpyPython/](../TqkLibraryScrcpyPython/), xoá bản v2.4.
- [ScrcpyServerConfig.py:32](../TqkLibraryScrcpyPython/Configs/ScrcpyServerConfig.py#L32): `"2.4"` → `"4.0"`.

Đây là handshake: server đọc tham số đầu tiên và tự thoát nếu version không khớp.

---

## 2. Nhóm B — bắt kịp `2.4` HEAD (2 commit Python còn thiếu)

### `c867cbb` — `ScrcpyDeployConfig`

Tách đường dẫn [adb](Glossary-vi.md#L5) / jar ra class riêng. Tạo
`TqkLibraryScrcpyPython/Configs/ScrcpyDeployConfig.py`:

| Field | Default |
|---|---|
| `AdbPath` | `"adb.exe"` |
| `ScrcpyServerPath` | `"scrcpy-server.jar"` |
| `ScrcpyServerAndroidPath` | `"/sdcard/scrcpy-server-tqk-{ver}.jar"` |
| `GetResolvedAndroidPath()` | thay `{ver}` bằng version server |

Kèm `TqkLibraryScrcpyPython/Constant.py` (mirror `Constant.cs`: `ScrcpyServerVersion`,
`ScrcpyServerAndroidPath`) để version chỉ khai báo ở một chỗ.

**Breaking:** `ScrcpyConfig.AdbPath` / `ScrcpyConfig.ScrcpyServerPath` bỏ đi, chuyển vào
`ScrcpyConfig.DeployConfig`.

### `1f009a0` — `PushServer` + `ForcePush`

- [Scrcpy.py:147-152](../TqkLibraryScrcpyPython/Scrcpy.py#L147-L152) và
  [Scrcpy.py:163-167](../TqkLibraryScrcpyPython/Scrcpy.py#L163-L167) đang **hardcode**
  `/sdcard/scrcpy-server-tqk.jar` ở cả lệnh push lẫn `CLASSPATH` → thay bằng `GetResolvedAndroidPath()`.
- Thêm `Scrcpy.PushServer(deployConfig=None) -> bool`.
- Thêm `ScrcpyConfig.ForcePush = True`; khi `False` thì `Connect` bỏ qua bước push (reconnect nhanh hơn,
  người gọi tự chịu trách nhiệm jar đã có trên máy).
- [Scrcpy.py:120](../TqkLibraryScrcpyPython/Scrcpy.py#L120) `self._adbPath = config.AdbPath` → `config.DeployConfig.AdbPath`.

---

## 3. Nhóm C — control protocol 4.0 (**rủi ro cao nhất**)

### Đánh số lại `ScrcpyControlType`

[ScrcpyControlType.py](../TqkLibraryScrcpyPython/Enums/ScrcpyControlType.py):

| Giá trị | Python hiện tại | 4.0 |
|---|---|---|
| 10 | `TYPE_SET_SCREEN_POWER_MODE` | `TYPE_SET_DISPLAY_POWER` |
| 14 | `OPEN_HARD_KEYBOARD_SETTINGS` | **`TYPE_UHID_DESTROY`** |
| 15 | — | `OPEN_HARD_KEYBOARD_SETTINGS` |
| 16–21 | — | `TYPE_START_APP`, `TYPE_RESET_VIDEO`, `TYPE_CAMERA_SET_TORCH`, `TYPE_CAMERA_ZOOM_IN`, `TYPE_CAMERA_ZOOM_OUT`, `TYPE_RESIZE_DISPLAY` |

Đây là chỗ nguy hiểm nhất của cả đợt nâng cấp: server **không validate** — gửi số cũ sang server 4.0
thì nó thực thi nhầm lệnh khác chứ không báo lỗi. Ví dụ `OpenHardKeyboardSetting()` hiện gửi `14`,
trên server 4.0 là `UHID_DESTROY`.

### Sửa encoder sẵn có — [ScrcpyControlHelper.py](../TqkLibraryScrcpyPython/Controls/ScrcpyControlHelper.py)

- **`inject_scroll_event`** ([L152-L175](../TqkLibraryScrcpyPython/Controls/ScrcpyControlHelper.py#L152-L175)) —
  range đổi `[-1, 1]` → `[-16, 16]`; chia 16 rồi clamp `[-1, 1]` trước khi
  [fixed-point](Glossary-vi.md#L58). Giữ nguyên code cũ ⇒ scroll trên scrcpy 3.3+ nhạy sai 16 lần.
- **`uhdi_create`** ([L254-L266](../TqkLibraryScrcpyPython/Controls/ScrcpyControlHelper.py#L254-L266)) —
  layout [UHID](Glossary-vi.md#L52) mới: `type, id(u16), vendorId(u16), productId(u16), nameLen(u8), name(UTF-8 ≤127), dataLen(u16), data`.
- **`set_screen_power_mode`** ([L207-L215](../TqkLibraryScrcpyPython/Controls/ScrcpyControlHelper.py#L207-L215)) →
  `set_display_power(on: bool)`, payload 1 byte `0/1`.
- **`inject_text`** ([L114](../TqkLibraryScrcpyPython/Controls/ScrcpyControlHelper.py#L114)) — C# dùng UTF-8,
  Python đang ép `encode('ascii')`. Sửa luôn cho khớp (lệch này có từ 2.4, không phải do 4.0).

### Encoder mới

`uhid_destroy(id)`, `start_app(name)` (1 byte len + UTF-8 ≤255, prefix `+` để force-stop),
`reset_video()`, `camera_set_torch(on)`, `camera_zoom_in()`, `camera_zoom_out()`,
`resize_display(width, height)` — 2 × u16, chỉ hợp lệ trên [flex display](Glossary-vi.md#L69).

### Lan sang tầng trên

- [ScrcpyControl.py:75-76](../TqkLibraryScrcpyPython/Controls/ScrcpyControl.py#L75-L76) — `SetScreenPowerMode` → `SetDisplayPower`, và thêm 6 method mới.
- [IControl.py](../TqkLibraryScrcpyPython/Interfaces/IControl.py) — cập nhật abstract method tương ứng.
- Xoá [ScrcpyScreenPowerMode.py](../TqkLibraryScrcpyPython/Enums/ScrcpyScreenPowerMode.py) + entry trong
  [Enums/\_\_init\_\_.py](../TqkLibraryScrcpyPython/Enums/__init__.py) và [\_\_init\_\_.py](../TqkLibraryScrcpyPython/__init__.py).

---

## 4. Nhóm D — option config mới (scrcpy 3.0 → 4.0)

### Vá `BaseConfig._get_argument` trước

[BaseConfig.py:79](../TqkLibraryScrcpyPython/Configs/BaseConfig.py#L79) chỉ nhận `bool / Enum / Rectangle / Size / int / str`.
`float` rơi hết xuống `return None` → mọi option float bị **nuốt im lặng**. C# đã vá ở `7d7f19f`
(`fix(config): emit float/double options from _GetArgument`). Cần thêm nhánh `float` (đặt trước
nhánh `int`, sau nhánh `bool` vì `bool` là subclass của `int` trong Python). Ảnh hưởng: `MaxFps`,
`CameraZoom`, `Angle`.

### [ScrcpyServerConfig.py](../TqkLibraryScrcpyPython/Configs/ScrcpyServerConfig.py)

| Property | Default | scrcpy |
|---|---|---|
| `ScreenOffTimeout` | `-1` | 3.0 |
| `NewDisplay` | `None` | 3.0 — [virtual display](Glossary-vi.md#L64) |
| `VdSystemDecorations` | `True` | 3.0 |
| `VdDestroyContent` | `True` | 3.1 |
| `DisplayImePolicy` | `None` | 3.2 |
| `KeepActive` | `False` | 4.0 |

`VdSystemDecorations` / `VdDestroyContent` phát tay `...=false` khi bằng `False` (giống C#).

### [VideoConfig.py](../TqkLibraryScrcpyPython/Configs/VideoConfig.py)

- **Xoá** `Orientation` + option `lock_video_orientation`, **xoá** [Orientations.py](../TqkLibraryScrcpyPython/Enums/Orientations.py).
- **Thêm** `CaptureOrientation: Optional[CaptureOrientations]` + `CaptureOrientationLock`, ghép thành
  `capture_orientation=[[@]<value>|@]`.
- `MaxFps`: `int` → `float`.
- **Thêm** `Angle: Optional[float]`, `MinSizeAlignment = 1`, `FlexDisplay = False`.

### [AudioConfig.py](../TqkLibraryScrcpyPython/Configs/AudioConfig.py)

Thêm `AudioSource: Optional[AudioSource]` (bỏ qua khi `Auto`) và `AudioDup = False`.

### [CameraConfig.py](../TqkLibraryScrcpyPython/Configs/CameraConfig.py)

Thêm `CameraZoom: float = 1` (chỉ phát khi `!= 1`) và `CameraTorch = False`.

### Enums

- **Thêm:** `CaptureOrientations` (`Orient0/90/180/270`, `Flip0/90/180/270`),
  `CaptureOrientationLock` (`Unlocked/LockedValue/LockedInitial`),
  `DisplayImePolicy` (`Local/Fallback/Hide`).
- **Sửa:** [AudioSource.py](../TqkLibraryScrcpyPython/Enums/AudioSource.py) thêm `Playback` (Android 13+).
- **Xoá:** `Orientations`, `ScrcpyScreenPowerMode`.
- Cập nhật [Enums/\_\_init\_\_.py](../TqkLibraryScrcpyPython/Enums/__init__.py) và [\_\_init\_\_.py](../TqkLibraryScrcpyPython/__init__.py).

⚠️ `CaptureOrientations` **không** map được bằng `.name.lower()` mặc định của `_get_argument`
(`Orient90` → phải ra `90`, `Flip90` → `flip90`) → phải truyền `formatter` riêng.

---

## 5. Nhóm E — `ListSupport` (port mới hoàn toàn)

Python chưa có gì trong mảng này. Cơ chế: push jar qua [adb](Glossary-vi.md#L5), chạy server với cờ
`list_*=true`, server in text ra stdout rồi thoát (không mở socket), client parse text. Hoàn toàn
độc lập với đường mirror/control — không đụng DLL native.

### File cần tạo

| File | Mirror từ C# |
|---|---|
| `ListSupport/ListSupportQuery.py` | `ListSupportQuery.cs` — kế thừa `BaseConfig`; giữ `DeployConfig` + 5 cờ `ListEncoders`/`ListDisplays`/`ListCameras`/`ListCameraSizes`/`ListApps`; `get_arguments()` phát version string trước tiên |
| `ListSupport/CodecInfo.py` | `Codec`, `Encoder` |
| `ListSupport/DisplayInfo.py` | `Display`, `Size` |
| `ListSupport/CameraInfo.py` | `CameraId`, `CameraFacing`, `IsHighSpeed`, `Size`, `FpsMin`, `FpsMax` |
| `ListSupport/AppInfo.py` | `Name`, `PackageName`, `IsSystem` (3.0+) |
| `ListSupport/ScrcpyServerListSupport.py` | parser + 5 list kết quả (`VideoCodecInfos`, `AudioCodecInfos`, `Displays`, `CameraInfos`, `Apps`) |
| `Helpers/AdbHelper.py` | `push_server()`, `run_server_with_adb()` — chạy adb, thu stdout/stderr |

Thêm `Scrcpy.ListSupport(query)` (bản C# là `ListSupportAsync`; phía Python dùng đồng bộ cho khớp
với `Connect`/`Stop` hiện có, `subprocess.run` + `capture_output`). Ném exception nếu stderr khác rỗng.

### Regex 4.0 khác 2.x — đây là chỗ dễ sai

Parser phải viết theo bản 4.0, **không** port bản 2.4:

- Tên encoder **không còn quote** và có hậu tố `(hw)`/`(sw)`/`[vendor]`/`(alias for ...)`
  → `--video-encoder='?([^'\s]+)'?`
- Dòng camera bỏ tiền tố `--video-source=camera`, chỉ còn `--camera-id=`
- Tập fps đổi `[15, 30]` → `{15, 30}` (4.0) → regex phải nhận cả `[...]` lẫn `{...}`
- 4.0 thêm hậu tố `, zoom-range=[...]` sau `fps=` → **không** anchor `\)` ngay sau fps
- `--list-apps`: tên app ≥30 ký tự làm package **xuống dòng** → cần state `pending_app`

Lấy nguyên bộ regex + nhánh xử lý từ
`D:\IT\Csharp\Libraries\TqkLibrary.Scrcpy\TqkLibrary.Scrcpy\ListSupport\ScrcpyServerListSupport.cs:21-32`
(bản 4.0), kèm luôn khối comment mẫu output để đối chiếu.

### Đường đẩy jar — C# đã vá, Python bám theo

Trước đây `Scrcpy.ListSupportAsync` bên C# hardcode `/sdcard/scrcpy-server-tqk.jar` trong khi
`Connect` dùng `/sdcard/scrcpy-server-tqk-{ver}.jar`. Commit `e5fdc6c`
(`fix(list-support)!: run ListSupportAsync from the configured server path`) đã vá: `ListSupportQuery`
giờ giữ `DeployConfig` thay cho `AdbPath`/`ScrcpyPath`, và `AdbHelper.PushServerAsync` nhận thẳng
`ScrcpyDeployConfig` + ném `ScrcpyException` khi adb exit code khác 0.

→ Python port đúng theo bản đã vá: cả `Connect` lẫn `ListSupport` dùng chung
`ScrcpyDeployConfig.GetResolvedAndroidPath()`. Kéo theo phải port cả `Exceptions/ScrcpyException.py`.

---

## 6. Nhóm F — test / đóng gói / tài liệu

- [test.py](../test.py): đường dẫn jar (L23), `AdbPath`/`ScrcpyServerPath` → `DeployConfig` (L22-23),
  `VideoConfig.Orientation` → `CaptureOrientation` (L35), bỏ `SetScreenPowerMode` (L83-84), thêm demo
  lệnh mới + demo `ListSupport`.
- [README.md](../README.md): hiện chỉ có 1 dòng tiêu đề. Cần bổ sung:
  yêu cầu (Windows x64, server 4.0), ví dụ tối thiểu, **bảng breaking change** (đã chốt breaking
  thẳng, không alias) và ghi chú chỗ Python cố ý lệch C# ở path jar của `ListSupport`.
- [pack.bat](../pack.bat) không cần sửa (đã copy toàn bộ package, chỉ loại `__pycache__`).

---

## 7. Thứ tự thực hiện

| # | Việc | Điều kiện xong |
|---|---|---|
| 1 | B1 rebuild DLL | DLL mới nằm trong `x64/`, `ctypes.CDLL` load được |
| 2 | B2 sửa struct | `ctypes.sizeof(...) == 20` |
| 3 | B3 jar + version | jar 4.0 có mặt, version string `"4.0"` |
| 4 | Nhóm B (`ScrcpyDeployConfig`, `PushServer`, `ForcePush`) | `Connect()` push đúng path `{ver}` |
| 5 | Nhóm C (control protocol) | so byte gói lệnh với C# 4.0 |
| 6 | Nhóm D (config) | so chuỗi `str(config)` với C# 4.0 cùng input |
| 7 | Nhóm E (ListSupport) | `ListSupport` trả đúng list trên thiết bị thật |
| 8 | Nhóm F (test/docs) | `test.py` chạy được, ảnh chụp đúng |

Bước 1–3 phải đi **cùng một lần commit**: đổi lẻ bất kỳ cái nào là hỏng runtime. Vì làm thẳng trên
`master`, nên trước khi bắt đầu hãy tag/ghi lại commit `8203cb7` để còn đường lùi về bản 2.4 chạy được.

Nhóm E chạy được **độc lập** với nhóm C/D (không đụng DLL, không đụng control protocol), nên nếu bước 1
kẹt vì môi trường build thì vẫn làm trước được.

**Kiểm chứng ưu tiên** cho bước 5-6: viết script so sánh — dựng cùng config ở C# và Python, in
`str(config)` / dump hex gói control, diff. Rẻ hơn nhiều so với debug trên thiết bị thật.

---

## 8. Rủi ro

| Rủi ro | Mức | Giảm thiểu |
|---|---|---|
| Không build được DLL (thiếu VS C++ workload / FFmpeg nuget) | **Cao** — chặn toàn bộ | Kiểm tra `Build.ps1` chạy được trước khi bắt đầu |
| Sai `ScrcpyControlType` → server làm nhầm lệnh, không báo lỗi | **Cao** | Dump hex đối chiếu C# |
| Struct lệch offset → giá trị rác vào native | **Cao** | Assert `sizeof` |
| `float` bị `_get_argument` nuốt im lặng | Trung bình | Unit test cho `_get_argument` |
| Breaking API (`AdbPath`, `SetScreenPowerMode`, `Orientations`) làm hỏng code người dùng | Trung bình | Đã chốt breaking thẳng → bảng breaking change trong README |
| Parser `ListSupport` viết theo format 2.x → không khớp output 4.0 | Trung bình | Port regex từ bản 4.0, giữ khối comment output mẫu để test |
| Làm thẳng `master`, giữa chừng repo không chạy được | Trung bình | Tag mốc `8203cb7` trước khi bắt đầu; gộp bước 1–3 vào 1 commit |
