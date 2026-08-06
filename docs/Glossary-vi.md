# Glossary (vi)

Giải thích các thuật ngữ chuyên ngành dùng trong trao đổi/tài liệu của project.

## adb

Android Debug Bridge — công cụ dòng lệnh của Android SDK để giao tiếp với thiết bị. Project dùng
`adb push` để đẩy file `scrcpy-server.jar` lên thiết bị, `adb reverse` để mở đường hầm ngược từ
thiết bị về PC, và `adb shell app_process` để chạy scrcpy server trên thiết bị.

## reverse tunnel

Đường hầm ngược do `adb reverse` tạo: thiết bị Android mở kết nối tới một `localabstract:` socket,
adb chuyển tiếp về cổng TCP trên PC. Nhờ vậy PC chỉ cần `listen` trên loopback, thiết bị là bên chủ
động `connect` — ngược với mô hình client/server thông thường.

## wire format

Định dạng byte thực tế truyền trên socket giữa scrcpy server (Android) và client (PC): thứ tự
trường, độ dài header, vị trí từng bit cờ. Đổi wire format là thay đổi phá vỡ tương thích — client
cũ đọc stream của server mới sẽ ra dữ liệu rác hoặc treo.

## demuxer

Thành phần đọc stream từ socket và tách ra từng gói (packet) media để đưa vào decoder. Trong project
là [wire format](#L17) của scrcpy được xử lý ở tầng C++ (`SocketWrapper::ReadPackage`, `Video::threadStart`).

## session header

Header 12 byte scrcpy 4.0 chèn vào đầu video stream và giữa các gói, phân biệt với gói media bằng
bit cao nhất của byte 0 (`header[0] & 0x80`). Nó mang width/height/`client_resized` và **không** kèm
payload, nên client phải nhận ra và bỏ qua thay vì coi là gói media.

## ABI

Application Binary Interface — hợp đồng ở mức nhị phân giữa hai module đã biên dịch: tên hàm export,
thứ tự tham số, và **layout struct** (offset từng field). Python gọi DLL C++ qua
[ctypes](#L41) nên struct khai báo phía Python phải khớp byte-for-byte với struct C++; lệch một
field là đọc/ghi sai vùng nhớ mà không có lỗi biên dịch nào cảnh báo.

## ctypes

Thư viện chuẩn của Python để gọi hàm trong DLL/shared library và khai báo struct C tương ứng
(`ctypes.Structure`). Không kiểm tra được [ABI](#L34) lúc chạy — sai layout sẽ gây lỗi ngầm.

## struct padding

Trình biên dịch C/C++ tự chèn byte đệm để mỗi field nằm ở offset chia hết cho kích thước của nó
(alignment). Ví dụ 6 field `bool` liên tiếp rồi tới `INT32` thì có 2 byte đệm. `ctypes.Structure`
mặc định áp dụng cùng quy tắc, nên chỉ cần khai báo đúng thứ tự và kiểu là khớp.

## UHID

User-space HID — cơ chế Linux/Android cho phép tạo thiết bị nhập liệu ảo (bàn phím, chuột, gamepad)
từ user space. scrcpy dùng để mô phỏng bàn phím/chuột vật lý thay vì inject event, cho trải nghiệm gõ
tiếng nước ngoài chính xác hơn.

## fixed-point 16

Cách mã hoá số thực bằng số nguyên 16 bit: giá trị `[0,1]` nhân 2^16 (unsigned 0.16, dùng cho
`pressure`), giá trị `[-1,1]` nhân 2^15 (signed 1.15, dùng cho `scroll`). scrcpy dùng để tránh gửi
float qua [wire format](#L17).

## virtual display

Màn hình ảo do scrcpy 3.0+ tạo trên thiết bị (`new_display=WxH/dpi`) thay vì mirror màn hình vật lý.
Ứng dụng chạy trên màn hình ảo không ảnh hưởng màn hình thật của thiết bị.

## flex display

[virtual display](#L64) được tạo với `flex_display=true` (scrcpy 4.0), cho phép đổi độ phân giải lúc
đang chạy qua control message `TYPE_RESIZE_DISPLAY`. Server từ chối lệnh resize trên display không
phải flex.
