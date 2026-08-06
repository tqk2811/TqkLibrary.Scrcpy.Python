# Mirror ListSupport/DisplayInfo.cs
from typing import Optional
from ..Structs.Size import Size


class DisplayInfo:
    def __init__(self, Display: Optional[str] = None, Size: Optional[Size] = None):
        self.Display: Optional[str] = Display
        self.Size = Size

    def __str__(self) -> str:
        w = self.Size.Width if self.Size else 0
        h = self.Size.Height if self.Size else 0
        return f"Display: {self.Display} - Size: {w}x{h}"

    __repr__ = __str__
