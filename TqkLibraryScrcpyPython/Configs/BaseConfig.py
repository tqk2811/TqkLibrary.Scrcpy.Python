from typing import Optional, Iterable, Callable, Any
from enum import Enum
from abc import ABC, abstractmethod
from ..Structs.Rectangle import Rectangle
from ..Structs.Size import Size

class BaseConfig(ABC):
    """
    Lớp cơ sở cho tất cả các Config.
    Cung cấp phương thức _get_argument() để tạo chuỗi tham số scrcpy.
    """

    @abstractmethod
    def get_arguments(self) -> Iterable[str]:
        """Phương thức bắt buộc để tạo danh sách các tham số dòng lệnh scrcpy."""
        # Phương thức này phải được triển khai trong các lớp con
        pass

    def _get_argument(
        self,
        option_name: str,
        value: Any,
        condition: Optional[Callable[[Any], bool]] = None,
        formatter: Optional[Callable[[Any], str]] = None,
    ) -> Optional[str]:
        # 0. Kiểm tra giá trị None (tương đương với việc C# fall-through các is type check)
        if value is None:
            return None
            
        # 1. Kiểm tra Condition/Validate (C# logic: validate is null || validate.Invoke(select))
        if condition is not None and not condition(value):
            return None # Trả về None (hoặc "") nếu điều kiện không thỏa mãn
        
        # 2. Xử lý Custom Formatter/Convert (C# logic: if (convert is not null))
        if formatter is not None:
            # C# return $"{optionNameAttribute?.Name}={convert(select)}";
            return f"{option_name}={formatter(value)}"
        
        # 3. Xử lý Default Conversion (Type-checking)
        
        # C# else if (select is bool b)
        if isinstance(value, bool):
             # C# return $"{optionNameAttribute.Name}={b.ToString().ToLower()}";
             return f"{option_name}={str(value).lower()}"
             
        # C# else if (select is Enum @enum)
        elif isinstance(value, Enum):
            # Dựa trên logic C# (ưu tiên attribute, nếu không có dùng giá trị int),
            # và dựa trên các ví dụ scrcpy (thường dùng tên string), ta sẽ ưu tiên
            # tên (name.lower()) và sau đó là giá trị số (.value).
            # Lưu ý: Đây là phần phức tạp nhất vì Python không có attribute trên Enum member
            # như C#. Ta tạm thời dùng .name.lower() cho các Enum có tên là string option
            # hoặc .value cho các Enum có giá trị là số option (như Orientations).
            
            # Nếu enum được gán tên rõ ràng (giả định), ta dùng tên.
            # Nếu không, ta dùng giá trị số.
            try:
                # Thử lấy giá trị name (thường dùng cho video_source=camera)
                return f"{option_name}={value.name.lower()}"
            except AttributeError:
                # Nếu không có .name (chẳng hạn IntEnum), thử lấy .value
                try:
                    return f"{option_name}={value.value}"
                except AttributeError:
                    # Trường hợp bất khả kháng, lấy giá trị string
                    return f"{option_name}={str(value).lower()}"
            
        # C# else if (select is Rectangle rect)
        elif isinstance(value, Rectangle):
            # C# return $"{optionNameAttribute.Name}={rect.Width}:{rect.Height}:{rect.X}:{rect.Y}";
            return f"{option_name}={value.Width}:{value.Height}:{value.X}:{value.Y}"
            
        # C# else if (select is Size size)
        elif isinstance(value, Size):
            # C# return $"{optionNameAttribute.Name}={size.Width}x{size.Height}";
            return f"{option_name}={value.Width}x{value.Height}"
            
        # C# else if (select is int i)
        elif isinstance(value, int):
            # C# return $"{optionNameAttribute.Name}={i}";
            return f"{option_name}={value}"
            
        # C# else if (select is string s)
        elif isinstance(value, str):
             # C# return $"{optionNameAttribute.Name}={s}";
             if value.strip(): # Chỉ trả về nếu string không rỗng
                 return f"{option_name}={value}"
             
        # C# return string.Empty;
        return None