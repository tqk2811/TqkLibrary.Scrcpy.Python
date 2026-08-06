# Mirror ListSupport/AppInfo.cs


class AppInfo:
    """Một app đã cài, lấy từ scrcpy --list-apps (scrcpy 3.0+)."""

    def __init__(self, Name: str = "", PackageName: str = "", IsSystem: bool = False):
        # Tên hiển thị (label) của app
        self.Name: str = Name
        # Tên package, vd com.android.settings
        self.PackageName: str = PackageName
        # True nếu là system app ('*' trong output scrcpy), False nếu là user app ('-')
        self.IsSystem: bool = IsSystem

    def __str__(self) -> str:
        return f"{'*' if self.IsSystem else '-'} {self.Name} ({self.PackageName})"

    __repr__ = __str__
