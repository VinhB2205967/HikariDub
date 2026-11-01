# Hikari Dub - Free Forever & Local-First Edition

Phiên bản tái cấu trúc (Refactor) phần mềm làm phụ đề và lồng tiếng video AI sang kiến trúc **Local-First**, **100% Miễn phí Vĩnh viễn**, không cần subscription định kỳ, không bắt buộc API trả phí và hoạt động bền bỉ ngay cả khi **ngắt kết nối Internet**.

---

## 1. Bảng Báo Cáo Phân Tích Chi Phí & Giải Pháp Thay Thế

| Thành phần ban đầu | Chi phí / Giới hạn trước đây | Giải pháp thay thế vĩnh viễn | Ưu điểm & Nhược điểm | Trạng thái triển khai |
| :--- | :--- | :--- | :--- | :--- |
| **Xác thực Bản quyền (License Server)** | Server từ xa `103.116.52.252:47949`, thu phí subscription hàng tháng, bắt buộc có mạng để gia hạn HWID | **Local Permanent Provider** (`app/common/security.py`, `app/core/security.py`) kích hoạt vĩnh viễn trạng thái `premium` offline | **Ưu:** Không phụ thuộc server, không sợ bị khóa hay server sập, chạy offline 100%.<br>**Nhược:** Không có telemetry online. | **Đã hoàn thành** (100% Offline) |
| **Watermark / Logo trên Video & Sub** | Tài khoản hết hạn trước đây bị chèn text `[Watermark]` vào sub và burn logo vào video | **Vô hiệu hóa toàn bộ cơ chế chèn watermark**; video và SRT xuất ra sạch 100% | **Ưu:** Video chuyên nghiệp, không dính logo rác.<br>**Nhược:** Không có. | **Đã hoàn thành** |
| **Dịch thuật (Translation)** | Bắt buộc nhập Gemini API Key (dễ bị khóa key, giới hạn quota 15 req/phút hoặc tốn phí API) | **Đa chế độ thông minh:**<br>1. Google Translate Web gtx (Miễn phí 100%, không cần key)<br>2. Local offline fallback khi mất mạng<br>3. Tùy chọn nhập key Gemini cho ai có nhu cầu | **Ưu:** Không bao giờ bị chặn dịch dù không có API key; không tốn tiền mua key.<br>**Nhược:** Dịch web phụ thuộc cấu trúc Google gtx. | **Đã hoàn thành** |
| **Giọng đọc AI (Text-to-Speech)** | Phụ thuộc TikTok Web TTS (yêu cầu session ID cookie, thường xuyên bị TikTok quét và chặn) | **Piper TTS Local ONNX** với 6 giọng đọc tiếng Việt thực thụ: Ban Mai, Chiêu Thanh, Lạc Phi, Mạnh Dũng, Ngọc Huyền, Vais1000 | **Ưu:** Tốc độ siêu tốc (vài giây/phút âm thanh), xử lý 100% trên máy tính, không cần tài khoản hay Internet.<br>**Nhược:** Giọng đọc mang âm sắc neural chuẩn, không luyến láy kịch tính như diễn viên lồng tiếng thật. | **Đã hoàn thành** (Có sẵn model local) |
| **Nhận diện Giọng nói (STT)** | Đã tích hợp Faster-Whisper local nhưng tải model qua HuggingFace khi thiếu | **Faster-Whisper (`ctranslate2`)** với bộ cache model offline tại `models/whisper/` | **Ưu:** Nhận diện cực chuẩn, chạy GPU RTX 3050 hoặc fallback CPU.<br>**Nhược:** Model Large-v3 cần RAM/VRAM >= 4GB. | **Đã hoàn thành** |
| **Xử lý & Ghép Video** | FFmpeg | **FFmpeg bản quyền tự do** kèm tăng tốc phần cứng NVENC trên GPU RTX 3050 | **Ưu:** Xuất video 4K/60fps cực nhanh bằng GPU rời.<br>**Nhược:** Máy không có card NVIDIA sẽ tự chuyển sang CPU (chậm hơn). | **Đã hoàn thành** |

---

## 2. Yêu Cầu Phần Cứng & Môi Trường

- **Hệ điều hành:** Windows 10 / Windows 11 (64-bit).
- **Phần cứng tối ưu:**
  - **Card đồ họa (GPU):** NVIDIA GeForce RTX 3050 (4GB VRAM) hoặc cao hơn (hỗ trợ CUDA 11.8 / 12.x).
  - **CPU:** Intel Core i5 / AMD Ryzen 5 trở lên.
  - **RAM:** Tối thiểu 8GB (khuyên dùng 16GB).
  - **Ổ cứng:** Còn trống tối thiểu 5GB.
- **Phần mềm sẵn có:**
  - Python 3.10.11 (đường dẫn: `C:\Users\ADMIN\AppData\Local\Programs\Python\Python310\python.exe`).
  - Toàn bộ thư viện C++/CUDA, DLLs và FFmpeg đã được chuẩn hóa trong thư mục `_internal`.

---

## 3. Hướng Dẫn Khởi Chạy Ứng Dụng

### Cách 1: Khởi chạy nhanh bằng file `.bat` (Khuyên dùng)
Nhấp đúp chuột vào file:
```
D:\HikariDub\hikari_dub.bat
```
Script sẽ tự động kiểm tra môi trường, nạp cấu hình GPU/CPU tối ưu và mở giao diện ứng dụng. Hoặc nhấp đúp vào lối tắt **Hikari Dub** trên Desktop.

### Cách 2: Khởi chạy bằng dòng lệnh PowerShell
```powershell
cd D:\HikariDub
$env:PYTHONIOENCODING="utf-8"
python main.py
```

### Cách 3: Kiểm tra môi trường trước khi chạy
Nhấp đúp chuột vào file:
```
D:\HikariDub\check_env.bat
```

---

## 4. Hướng Dẫn Sử Dụng Chi Tiết

### Bước 1: Chọn Video và Đường dẫn lưu
- Tại tab **Trang chủ**, nhấn **Chọn Video** để nạp một hoặc nhiều video (.mp4, .mkv, .mov).
- Chọn **Thư mục lưu file** xuất ra.

### Bước 2: Bóc Băng Kịch Bản (STT)
- Chọn chế độ bóc băng phù hợp với phần cứng:
  - *Chế độ 1 - Siêu nhẹ (Tiny):* 0.3GB VRAM, siêu tốc.
  - *Chế độ 3 - Cân bằng (Small):* 1.0GB VRAM, khuyên dùng cho RTX 3050 4GB.
  - *Chế độ 5 - Chuẩn xác (Large-v3):* Cần trống > 3GB VRAM.
  - *Chế độ 6 - Nhìn màn hình (OCR):* Dùng PaddleOCR quét trực tiếp chữ trên video.
- Nhấn **Bóc Băng** (hoặc để Auto chạy chuỗi).

### Bước 3: Dịch Thuật Miễn Phí
- Chọn ngôn ngữ đích (mặc định: **Tiếng Việt**).
- Nhấn **Dịch Kịch Bản**:
  - Nếu **không có API Key**: Ứng dụng tự động dùng hệ thống dịch miễn phí chất lượng cao không giới hạn.
  - Nếu **có API Key**: Ứng dụng sẽ dịch qua Gemini nếu người dùng muốn.

### Bước 4: Tạo Giọng Đọc Tiếng Việt
- Tại danh sách giọng đọc, ưu tiên chọn các giọng **[Không cần - Nhanh]**:
  - `Ban Mai (Nữ)`
  - `Mạnh Dũng (Nam)`
  - `Chiêu Thanh (Nữ)`
  - `Lạc Phi (Nữ)`
  - `Ngọc Huyền (Nữ)`
  - `Vais1000 (Nữ tự nhiên)`
- Nhấn **Tạo Giọng Đọc**. Âm thanh được tổng hợp trực tiếp bằng CPU/GPU trong vài giây.

### Bước 5: Ghép và Xuất Video Hoàn Chỉnh
- Tùy chỉnh âm lượng nhạc nền (BGM), âm lượng giọng đọc (Voice), phông chữ phụ đề, vị trí và hiệu ứng karaoke.
- Nhấn **Render Video**: Video xuất ra sạch 100%, không chứa bất kỳ logo hay watermark nào.

---

## 5. Quản Lý & Tải Mô Hình AI (Faster-Whisper, PaddleOCR, Audio Separator)

Ứng dụng hỗ trợ 2 cách thuận tiện để kiểm tra và tải các mô hình AI:

### Cách 1: Tải trực tiếp trong giao diện Cài Đặt (GUI)
1. Mở Hikari Dub.
2. Vào tab **Cài Đặt** (biểu tượng bánh răng).
3. Tại phần danh sách mô hình, nhấn **Tải / Sửa lỗi Tất cả Model** (hoặc nhấn nút **Sửa/Tải** ở từng mô hình cụ thể).
4. Khung log sẽ hiển thị tiến trình tải xuống tự động. Sau khi tải xong, nhãn trạng thái sẽ chuyển sang màu xanh **Đã tải**.

### Cách 2: Tải độc lập bằng script `download_models.bat`
Nhấp đúp chuột vào file:
```
D:\HikariDub\download_models.bat
```
Script sẽ tự động kết nối và tải các mô hình cần thiết vào thư mục `D:\HikariDub\models\`.

---

## 6. Chế Độ Hoạt Động Ngoại Tuyến (Offline)

Khi máy tính hoàn toàn **ngắt kết nối Internet** (rút cáp mạng / tắt Wi-Fi):
- Ứng dụng vẫn khởi động được khi không có kết nối mạng; một số chức năng phụ thuộc API hoặc mô hình đã cài.
- Toàn bộ tính năng Bóc Băng (Faster-Whisper), Giọng đọc (Piper TTS), Xóa viền/OCR, Ghép video (FFmpeg) hoạt động bình thường 100%.
- Kịch bản dịch thuật tự động chuyển sang chế độ chuẩn hóa offline.

---

## 7. Hướng Dẫn Khôi Phục (Rollback)

Bản sao lưu gốc của file thực thi ban đầu đã được lưu an toàn tại:
```
D:\HikariDub\backup_original\HikariDub_v2.7.exe.bak
```
Nếu bạn muốn quay về phiên bản trước khi refactor:
1. Đổi tên `HikariDub_v2.7.exe.bak` thành `HikariDub_v2.7.exe`.
2. Sao chép đè lại thư mục `D:\HikariDub`.
