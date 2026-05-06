import typing
from typing import Any, List, Callable

from ..Enums.ScrcpyDisconnectSource import ScrcpyDisconnectSource

if typing.TYPE_CHECKING:
    from ..Interfaces import IScrcpy
else:
    IScrcpy = Any

DisconnectHandler = Callable[[IScrcpy, ScrcpyDisconnectSource], None]


class DisconnectEvent:
    def __init__(self, name: str = "Event"):
        self.name: str = name
        self._handlers: List[DisconnectHandler] = []

    def Register(self, handler: DisconnectHandler) -> None:
        if handler not in self._handlers:
            self._handlers.append(handler)

    def Unregister(self, handler: DisconnectHandler) -> None:
        if handler in self._handlers:
            self._handlers.remove(handler)

    def Fire(self, scrcpy: IScrcpy, source: ScrcpyDisconnectSource) -> None:
        for handler in list(self._handlers):
            try:
                handler(scrcpy, source)
            except Exception as e:
                print(f"Lỗi khi thực thi handler {handler.__name__} trong sự kiện {self.name}: {e}")
