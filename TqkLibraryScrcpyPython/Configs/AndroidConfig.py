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
        # --show_touches (C# default condition: value == true)
        yield self._get_argument("show_touches", self.ShowTouches)
        
        # --stay-awake
        yield self._get_argument("stay_awake", self.StayAwake)
        
        # --power_off_on_close
        yield self._get_argument("power_off_on_close", self.PowerOffOnClose)
        
        # --power_on
        yield self._get_argument("power_on", self.PowerOn)