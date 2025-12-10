# Tên file gốc: ScrcpyScreenPowerMode.cs
from enum import Enum

class ScrcpyScreenPowerMode(Enum):
    """
    TqkLibrary.Scrcpy.Enums.ScrcpyScreenPowerMode
    https://github.com/Genymobile/scrcpy/blob/ce43fad645d4eb30f322dbeb50d5197601564931/server/src/main/java/com/genymobile/scrcpy/Device.java#L25
    Kiểu cơ sở: byte
    """
    # Display power mode off: used while blanking the screen.
    POWER_MODE_OFF = 0
    # Display power mode doze: used while putting the screen into low power mode.
    POWER_MODE_DOZE = 1
    # Display power mode normal: used while unblanking the screen.
    POWER_MODE_NORMAL = 2
    # Display power mode doze: used while putting the screen into a suspended low power mode.
    POWER_MODE_DOZE_SUSPEND = 3
    # Display power mode on: used while putting the screen into a suspended full power mode.
    POWER_MODE_ON_SUSPEND = 4