# TqkLibrary.Scrcpy.Python/Configs/AndroidConfig.py

from typing import Iterable
from .BaseConfig import BaseConfig

class AndroidConfig(BaseConfig):

    def __init__(self):
        self.ShowTouches: bool = False
        self.StayAwake: bool = True
        self.PowerOffOnClose: bool = False
        self.PowerOn: bool = True

    def get_arguments(self) -> Iterable[str]:
        # show_touches=true chỉ phát khi True (default false)
        yield self._get_argument("show_touches", self.ShowTouches, condition=lambda x: x)
        # stay_awake=true chỉ phát khi True (default false phia scrcpy)
        yield self._get_argument("stay_awake", self.StayAwake, condition=lambda x: x)
        # power_off_on_close=true chỉ phát khi True
        yield self._get_argument("power_off_on_close", self.PowerOffOnClose, condition=lambda x: x)
        # power_on=false chỉ phát khi False (server default true)
        yield self._get_argument("power_on", self.PowerOn, condition=lambda x: not x)