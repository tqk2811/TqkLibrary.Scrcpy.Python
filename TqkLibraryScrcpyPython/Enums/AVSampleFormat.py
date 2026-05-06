from enum import IntEnum


class AVSampleFormat(IntEnum):
    """Audio sample formats, matching FFmpeg AVSampleFormat values."""
    U8 = 0
    S16 = 1
    S32 = 2
    FLT = 3
    DBL = 4
    U8P = 5
    S16P = 6
    S32P = 7
    FLTP = 8
    DBLP = 9
    S64 = 10
    S64P = 11
