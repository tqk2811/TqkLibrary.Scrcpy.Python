class Rectangle:
    """Mô phỏng System.Drawing.Rectangle"""
    def __init__(self, x: int, y: int, width: int, height: int):
        self.X = x
        self.Y = y
        self.Width = width
        self.Height = height
    def __str__(self):
        return f"{self.X}:{self.Y}:{self.Width}:{self.Height}"