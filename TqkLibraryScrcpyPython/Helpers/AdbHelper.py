# TqkLibrary.Scrcpy.Python/Helpers/AdbHelper.py
# Mirror Helpers/AdbHelper.cs

import subprocess
from typing import NamedTuple, Optional
from ..Configs.ScrcpyDeployConfig import ScrcpyDeployConfig
from ..Exceptions import ScrcpyException


class ProcessStd(NamedTuple):
    StdOut: str
    StdErr: str


def _creation_flags() -> int:
    return getattr(subprocess, "CREATE_NO_WINDOW", 0)


def push_server(
        deploy_config: ScrcpyDeployConfig,
        device_id: str,
        timeout_sec: Optional[float] = None) -> None:
    """Đẩy ScrcpyServerPath lên GetResolvedAndroidPath() — đúng path mà Connect() chạy server từ đó.

    Raise ScrcpyException nếu adb push trả exit code khác 0. Không check thì lệnh app_process
    sau đó chạy trên một jar có thể không tồn tại, và lỗi hiện ra dưới dạng lỗi lạ từ server
    thay vì lỗi push thật sự.
    """
    android_path = deploy_config.GetResolvedAndroidPath()
    result = subprocess.run(
        [deploy_config.AdbPath, "-s", device_id, "push",
         deploy_config.ScrcpyServerPath, android_path],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout_sec,
        creationflags=_creation_flags(),
    )
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        raise ScrcpyException(
            f"adb push failed (exit {result.returncode}): "
            f"'{deploy_config.ScrcpyServerPath}' -> '{android_path}'. {stderr}"
        )


def run_server_with_adb(
        adb_path: str,
        device_id: str,
        argument: list,
        timeout_sec: Optional[float] = None) -> ProcessStd:
    """Chạy `adb -s <device> <argument...>` và thu stdout/stderr."""
    result = subprocess.run(
        [adb_path, "-s", device_id] + list(argument),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout_sec,
        creationflags=_creation_flags(),
    )
    return ProcessStd(
        StdOut=result.stdout.decode("utf-8", errors="replace"),
        StdErr=result.stderr.decode("utf-8", errors="replace"),
    )
