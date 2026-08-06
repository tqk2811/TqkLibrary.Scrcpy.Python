# TqkLibrary.Scrcpy.Python/Constant.py
# Mirror Constant.cs

# Version string gửi cho server, phải khớp scrcpy-server.jar đang deploy.
ScrcpyServerVersion: str = "4.0"

# {ver} được thay bằng ScrcpyServerVersion để jar khác version không đè lên nhau trên thiết bị.
ScrcpyServerAndroidPath: str = "/sdcard/scrcpy-server-tqk-{ver}.jar"
