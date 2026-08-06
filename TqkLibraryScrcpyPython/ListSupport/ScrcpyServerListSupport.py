# Mirror ListSupport/ScrcpyServerListSupport.cs

import re
from typing import List, Optional
from ..Structs.Size import Size
from ..Enums.CameraFacing import CameraFacing
from .CodecInfo import CodecInfo
from .DisplayInfo import DisplayInfo
from .CameraInfo import CameraInfo
from .AppInfo import AppInfo


# Regex chịu được output --list-* của cả scrcpy 2.x lẫn 3.0+/4.0:
#  - tên encoder: có quote ('name', scrcpy 2.x) HOẶC không quote kèm hậu tố " (hw)/(sw) [vendor]"
#    (scrcpy 3.0+, commit acff5b00)
#  - tập fps camera: "[15, 30]" (<=3.3.4) HOẶC "{15, 30}" (4.0, commit af355804);
#    có thể kèm hậu tố ", zoom-range=[...]" (4.0)
_regex_video = re.compile(r"--video-codec=(\S+) --video-encoder='?([^'\s]+)'?")
_regex_audio = re.compile(r"--audio-codec=(\S+) --audio-encoder='?([^'\s]+)'?")
_regex_display = re.compile(r"--display-id=(\d+) +\((\d+)x(\d+)\)")
_regex_camera = re.compile(r"--camera-id=(\d+) +\((\S+), (\d+)x(\d+), fps=[\[{]([0-9 ,]+)[\]}]")
_regex_camera_size = re.compile(r"- (\d+)x(\d+)")
_regex_camera_fps = re.compile(r"\(fps=[\[{]([0-9 ,]+)[\]}]\)")
# --list-apps (scrcpy 3.0+): " * <Name căn lề 30> <package>" (system) / " - <Name> <package>" (user).
# Khi tên dài >= 30 ký tự thì package rớt xuống dòng kế tiếp.
_regex_app = re.compile(r"^([*-]) (.+?)\s{2,}(\S+)$")
_regex_app_name_only = re.compile(r"^([*-]) (\S.*)$")
_regex_app_package = re.compile(r"^[\w.]+$")


class ScrcpyServerListSupport:
    """Kết quả parse output --list-* của scrcpy server."""

    def __init__(self):
        self.Videos: List[CodecInfo] = []
        self.Audios: List[CodecInfo] = []
        self.Displays: List[DisplayInfo] = []
        self.CameraInfos: List[CameraInfo] = []
        # App đã cài, lấy từ --list-apps (scrcpy 3.0+)
        self.Apps: List[AppInfo] = []

    @staticmethod
    def Parse(data: str) -> "ScrcpyServerListSupport":
        """
        Output mẫu (scrcpy 4.0):

        [server] INFO: Device: [Xiaomi] Redmi Redmi Note 9S (Android 12)
        [server] INFO: List of video encoders:
            --video-codec=h264 --video-encoder=OMX.qcom.video.encoder.avc     (hw) [vendor]
            --video-codec=h264 --video-encoder=c2.android.avc.encoder         (sw)
        [server] INFO: List of audio encoders:
            --audio-codec=opus --audio-encoder=c2.android.opus.encoder        (sw)
        [server] INFO: List of displays:
            --display-id=0    (1080x2400)
        [server] INFO: List of cameras:
            --camera-id=0    (back, 4000x3000, fps=[15, 30])
                - 3840x2160
              High speed capture (--camera-high-speed):
                - 1280x720 (fps=[120, 240])
        """
        datas = [x.strip() for x in re.split(r"[\r\n]", data) if x and x.strip()]

        result = ScrcpyServerListSupport()
        l_current = ""
        is_camera_high_speed = False
        camera_info_current: Optional[CameraInfo] = None
        pending_app: Optional[AppInfo] = None  # app có tên bị wrap (package nằm ở dòng sau)

        for d in datas:
            if d.startswith("[server] INFO: List of"):
                l_current = d

            match = _regex_video.search(d)
            if match:
                result.Videos.append(CodecInfo(Codec=match.group(1), Encoder=match.group(2)))
                continue

            match = _regex_audio.search(d)
            if match:
                result.Audios.append(CodecInfo(Codec=match.group(1), Encoder=match.group(2)))
                continue

            match = _regex_display.search(d)
            if match:
                result.Displays.append(DisplayInfo(
                    Display=match.group(1),
                    Size=Size(int(match.group(2)), int(match.group(3))),
                ))
                continue

            if "cameras:" in l_current:
                match = _regex_camera.search(d)
                if match:
                    fps = [x.strip() for x in match.group(5).split(",")]
                    is_camera_high_speed = False  # reset
                    camera_info_current = CameraInfo(
                        CameraId=int(match.group(1)),
                        CameraFacing=CameraFacing[match.group(2).capitalize()],
                        FpsMin=int(fps[0]),
                        FpsMax=int(fps[-1]),
                    )
                elif "--camera-high-speed" in d:
                    is_camera_high_speed = True
                else:
                    match = _regex_camera_size.search(d)
                    if match:
                        if camera_info_current is None:
                            raise RuntimeError("camera size line before any --camera-id line")
                        camera_info = CameraInfo(
                            CameraId=camera_info_current.CameraId,
                            CameraFacing=camera_info_current.CameraFacing,
                            FpsMin=camera_info_current.FpsMin,
                            FpsMax=camera_info_current.FpsMax,
                            Size=Size(int(match.group(1)), int(match.group(2))),
                            IsHighSpeed=is_camera_high_speed,
                        )

                        match = _regex_camera_fps.search(d)
                        if match:
                            fps = [x.strip() for x in match.group(1).split(",")]
                            camera_info.FpsMin = int(fps[0])
                            camera_info.FpsMax = int(fps[-1])
                        result.CameraInfos.append(camera_info)

            elif "apps:" in l_current:
                app_match = _regex_app.match(d)
                if app_match:
                    result.Apps.append(AppInfo(
                        IsSystem=app_match.group(1) == "*",
                        Name=app_match.group(2).strip(),
                        PackageName=app_match.group(3),
                    ))
                    pending_app = None
                else:
                    app_match = _regex_app_name_only.match(d)
                    if app_match:
                        # tên dài (>= 30 ký tự): package rớt xuống dòng sau
                        pending_app = AppInfo(
                            IsSystem=app_match.group(1) == "*",
                            Name=app_match.group(2).strip(),
                        )
                    elif pending_app is not None and _regex_app_package.match(d):
                        pending_app.PackageName = d
                        result.Apps.append(pending_app)
                        pending_app = None

        return result
