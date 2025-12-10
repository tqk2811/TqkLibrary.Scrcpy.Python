class Size:
    """Mô phỏng System.Drawing.Size"""
    def __init__(self, width: int, height: int):
        self.Width = width
        self.Height = height
    def __str__(self):
        return f"{self.Width}x{self.Height}"