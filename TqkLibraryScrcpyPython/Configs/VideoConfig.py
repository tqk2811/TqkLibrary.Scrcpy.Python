# TqkLibrary.Scrcpy.Python/Configs/VideoConfig.py

from typing import Optional, Iterable
from .BaseConfig import BaseConfig
from ..Structs.Rectangle import Rectangle 
from ..Enums.Orientations import Orientations 

class VideoConfig(BaseConfig):

    def __init__(self):
        self.DisplayId: Optional[int] = None
        self.Orientation: Orientations = Orientations.Auto
        self.MaxFps: int = 0
        self.VideoBitrate: int = 0
        self.VideoCodec: Optional[str] = None
        self.VideoCodecOption: Optional[str] = None
        self.VideoEncoder: Optional[str] = None
        self.Crop: Optional[Rectangle] = None
        self.DownsizeOnError: bool = True

    def get_arguments(self) -> Iterable[str]:
        # --display-id (C# condition: x.HasValue)
        yield self._get_argument(
            "display_id", 
            self.DisplayId, 
            condition=lambda x: x is not None 
        )
        
        # --lock-video-orientation (C# condition: x != Orientations.Auto)
        yield self._get_argument(
            "lock_video_orientation", 
            self.Orientation, 
            condition=lambda x: x != Orientations.Auto,
            formatter=lambda x: x.value
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