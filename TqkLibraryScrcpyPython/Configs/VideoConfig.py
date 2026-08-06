# TqkLibrary.Scrcpy.Python/Configs/VideoConfig.py

from typing import Optional, Iterable
from .BaseConfig import BaseConfig
from ..Structs.Rectangle import Rectangle
from ..Enums.CaptureOrientations import CaptureOrientations
from ..Enums.CaptureOrientationLock import CaptureOrientationLock


class VideoConfig(BaseConfig):

    def __init__(self):
        self.DisplayId: Optional[int] = None

        # Hướng capture (scrcpy 3.0). Ghép với CaptureOrientationLock thành option
        # capture_orientation. None = bỏ qua (mặc định server).
        # Thay cho LockVideoOrientation/Orientations của scrcpy 2.x (đã bị bỏ ở 3.0).
        self.CaptureOrientation: Optional[CaptureOrientations] = None

        # Chế độ khoá cho CaptureOrientation.
        self.CaptureOrientationLock: CaptureOrientationLock = CaptureOrientationLock.Unlocked

        # Default: 0 (không giới hạn). scrcpy 4.0 nhận số thực.
        self.MaxFps: float = 0

        self.VideoBitrate: int = 0
        self.VideoCodec: Optional[str] = None
        self.VideoCodecOption: Optional[str] = None
        self.VideoEncoder: Optional[str] = None
        self.Crop: Optional[Rectangle] = None
        self.DownsizeOnError: bool = True

        # Xoay video theo góc (độ, nhận số thực). None = bỏ qua.
        self.Angle: Optional[float] = None

        # Làm tròn kích thước video xuống bội số của giá trị này (phải là 1, 2, 4, 8 hoặc 16).
        # Default: 1 (bỏ qua). scrcpy 4.0
        self.MinSizeAlignment: int = 1

        # Cho phép đổi độ phân giải display ảo lúc đang chạy (flex display).
        # Bắt buộc bật nếu muốn dùng Control.ResizeDisplay(). scrcpy 4.0
        self.FlexDisplay: bool = False

    def get_arguments(self) -> Iterable[str]:
        # --display-id (C# condition: x.HasValue)
        yield self._get_argument(
            "display_id",
            self.DisplayId,
            condition=lambda x: x is not None
        )

        # --max-fps (C# condition: x > 0)
        yield self._get_argument(
            "max_fps",
            self.MaxFps,
            condition=lambda x: x > 0
        )

        # --video-bit-rate (C# condition: x > 0)
        yield self._get_argument(
            "video_bit_rate",
            self.VideoBitrate,
            condition=lambda x: x > 0
        )

        # --video-codec (C# condition: !string.IsNullOrWhiteSpace)
        yield self._get_argument(
            "video_codec",
            self.VideoCodec,
            condition=lambda x: bool(x and str(x).strip())
        )

        # --video-codec-options
        yield self._get_argument(
            "video_codec_options",
            self.VideoCodecOption,
            condition=lambda x: bool(x and str(x).strip())
        )

        # --video-encoder
        yield self._get_argument(
            "video_encoder",
            self.VideoEncoder,
            condition=lambda x: bool(x and str(x).strip())
        )

        # --crop (C# condition: x.HasValue)
        yield self._get_argument(
            "crop",
            self.Crop,
            condition=lambda x: x is not None
        )

        # --downsize-on-error (C# condition: !x) -> Tạo tham số nếu là False
        yield self._get_argument(
            "downsize_on_error",
            self.DownsizeOnError,
            condition=lambda x: not x
        )

        # scrcpy 4.0
        yield self._get_argument(
            "min_size_alignment",
            self.MinSizeAlignment,
            condition=lambda x: x > 1
        )
        yield self._get_argument("flex_display", self.FlexDisplay, condition=lambda x: x)

        # capture_orientation: [[@]<value>|@]
        # LockedInitial phát ra "@" trơ, không kèm giá trị.
        if (self.CaptureOrientation is not None
                or self.CaptureOrientationLock == CaptureOrientationLock.LockedInitial):
            value = ""
            if self.CaptureOrientationLock in (CaptureOrientationLock.LockedValue,
                                               CaptureOrientationLock.LockedInitial):
                value += "@"
            if self.CaptureOrientation is not None:
                value += self.CaptureOrientation.to_option()
            yield f"capture_orientation={value}"

        # angle
        if self.Angle is not None:
            yield self._get_argument("angle", float(self.Angle))
