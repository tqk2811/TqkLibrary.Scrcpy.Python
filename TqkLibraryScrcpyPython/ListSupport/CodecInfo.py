# Mirror ListSupport/CodecInfo.cs
from typing import Optional


class CodecInfo:
    def __init__(self, Codec: Optional[str] = None, Encoder: Optional[str] = None):
        self.Codec: Optional[str] = Codec
        self.Encoder: Optional[str] = Encoder

    def __str__(self) -> str:
        return f"Codec: {self.Codec} - Encoder: {self.Encoder}"

    __repr__ = __str__
