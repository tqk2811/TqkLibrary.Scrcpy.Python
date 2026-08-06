# TqkLibrary.Scrcpy.Python/Configs/AudioConfig.py

from typing import Optional, Iterable
from .BaseConfig import BaseConfig
from ..Enums.AudioSource import AudioSource

class AudioConfig(BaseConfig):

    def __init__(self):
        self.IsAudio: bool = False
        self.AudioBitrate: int = 0
        self.AudioCodec: Optional[str] = None
        self.AudioCodecOption: Optional[str] = None
        self.AudioEncoder: Optional[str] = None

        # Nguồn audio. None/Auto = bỏ qua (server tự chọn).
        # Dùng AudioSource.Playback để thu audio đang phát mà không tắt tiếng thiết bị (Android 13+).
        self.AudioSource: Optional[AudioSource] = None

        # Phát audio ra cả scrcpy lẫn loa thiết bị cùng lúc.
        self.AudioDup: bool = False

    def get_arguments(self) -> Iterable[str]:
        # --audio (C# default condition: value == true)
        yield self._get_argument("audio", self.IsAudio)

        # --audio_bit_rate (C# condition: IsAudio && x > 0)
        yield self._get_argument(
            "audio_bit_rate", 
            self.AudioBitrate, 
            condition=lambda x: self.IsAudio and x > 0
        )
        
        # --audio_codec (C# condition: IsAudio && !string.IsNullOrWhiteSpace(x))
        yield self._get_argument(
            "audio_codec", 
            self.AudioCodec, 
            condition=lambda x: self.IsAudio and bool(x and str(x).strip())
        )

        # --audio_codec_options
        yield self._get_argument(
            "audio_codec_options", 
            self.AudioCodecOption, 
            condition=lambda x: self.IsAudio and bool(x and str(x).strip())
        )

        # --audio_encoder
        yield self._get_argument(
            "audio_encoder",
            self.AudioEncoder,
            condition=lambda x: self.IsAudio and bool(x and str(x).strip())
        )

        # --audio-source (scrcpy 4.0; Auto = để server tự chọn nên không phát)
        yield self._get_argument(
            "audio_source",
            self.AudioSource,
            condition=lambda x: self.IsAudio and x is not None and x != AudioSource.Auto,
            formatter=lambda x: x.name.lower(),
        )

        # --audio-dup (scrcpy 4.0)
        yield self._get_argument(
            "audio_dup",
            self.AudioDup,
            condition=lambda x: self.IsAudio and x,
        )