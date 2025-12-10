import typing
from typing import Any, List, Dict, Callable

if typing.TYPE_CHECKING:
    from ..Interfaces import IScrcpy
else:
    IScrcpy = Any

# Định nghĩa kiểu cho Handler không tham số
ClipboardHandler = Callable[[IScrcpy,str], None]

class ClipboardEvent:    
    def __init__(self, name: str = "Event"):
        self.name: str = name
        self._handlers: List[ClipboardHandler] = []

    def Register(self, handler: ClipboardHandler) -> None:
        if handler not in self._handlers:
            self._handlers.append(handler)

    def Unregister(self, handler: ClipboardHandler) -> None:
        if handler in self._handlers:
            self._handlers.remove(handler)

    def Fire(self, scrcpy: IScrcpy, text: str) -> None:
        for handler in list(self._handlers): 
            try:
                handler(scrcpy, text)
            except Exception as e:
                print(f"Lỗi khi thực thi handler {handler.__name__} trong sự kiện {self.name}: {e}")