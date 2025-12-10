# TqkLibrary.Scrcpy.Python/Configs/AudioConfig.py

from typing import Optional, Iterable
from .BaseConfig import BaseConfig

class AudioConfig(BaseConfig):
    
    IsAudio: bool = False
    AudioBitrate: int = 0
    AudioCodec: Optional[str] = None
    AudioCodecOption: Optional[str] = None
    AudioEncoder: Optional[str] = None

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