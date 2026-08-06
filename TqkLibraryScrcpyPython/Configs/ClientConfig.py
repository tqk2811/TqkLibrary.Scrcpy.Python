# TqkLibrary.Scrcpy.Python/Configs/ClientConfig.py

from ..Enums.FFmpegAVHWDeviceType import FFmpegAVHWDeviceType
from ..Enums.D3D11Filter import D3D11Filter


class ClientConfig:
    """Tuá»³ chá»n giáº£i mÃ£/render phÃ­a client (PC).

    KhÃ¡c vá»›i ScrcpyServerConfig (tham sá»‘ gá»­i cho server trÃªn thiáº¿t bá»‹) vÃ  ScrcpyDeployConfig
    (Ä‘Æ°á»ng dáº«n adb/jar): cÃ¡c tuá»³ chá»n á»Ÿ Ä‘Ã¢y chá»‰ áº£nh hÆ°á»Ÿng cÃ¡ch DLL native dá»±ng vÃ  chuyá»ƒn Ä‘á»•i
    hÃ¬nh áº£nh trÃªn mÃ¡y tÃ­nh, khÃ´ng gá»­i gÃ¬ xuá»‘ng thiáº¿t bá»‹.
    """

    def __init__(self):
        # DÃ¹ng D3D11 Ä‘á»ƒ render UI.
        # Chá»‰ cháº¡y vá»›i HwType lÃ  AV_HWDEVICE_TYPE_D3D11VA hoáº·c AV_HWDEVICE_TYPE_NONE.
        self.IsUseD3D11ForUiRender: bool = False

        # DÃ¹ng D3D11 Ä‘á»ƒ convert áº£nh.
        # Muá»‘n báº­t thÃ¬ pháº£i Ä‘áº·t IsUseD3D11ForUiRender = True vÃ  HwType = AV_HWDEVICE_TYPE_NONE.
        self.IsUseD3D11ForConvert: bool = False

        # Chá»‰ cÃ³ tÃ¡c dá»¥ng khi HwType = AV_HWDEVICE_TYPE_D3D11VA.
        self.Filter: D3D11Filter = D3D11Filter.D3D11_FILTER_MIN_MAG_LINEAR_MIP_POINT

        # TÄƒng tá»‘c pháº§n cá»©ng cho viá»‡c giáº£i mÃ£ áº£nh.
        self.HwType: FFmpegAVHWDeviceType = FFmpegAVHWDeviceType.AV_HWDEVICE_TYPE_NONE

        # Flush D3D11 device sau má»—i láº§n váº½ UI Ä‘á»ƒ frame Ä‘Æ°á»£c submit trÆ°á»›c khi surface queue
        # present nÃ³. Render dÃ¹ng D3D11 device khÃ¡c vá»›i producer cá»§a surface queue, nÃªn thiáº¿u
        # cá» nÃ y thÃ¬ má»™t láº§n present Ä‘Æ¡n láº» (vd resize cá»­a sá»• lÃºc device Ä‘ang ráº£nh) cÃ³ thá»ƒ ra
        # mÃ n hÃ¬nh Ä‘en. Chá»‰ cÃ³ tÃ¡c dá»¥ng khi IsUseD3D11ForUiRender = True.
        self.IsForceUiGpuFlush: bool = True
