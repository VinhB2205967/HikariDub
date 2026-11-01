# Hikari Dub - AI Dubbing Studio (Local-First Edition)

Phần mềm tạo phụ đề tự động và lồng tiếng video bằng trí tuệ nhân tạo (AI), kiến trúc **Local-First**, hỗ trợ xử lý ngoại tuyến (Offline), không watermark và tối ưu hóa tăng tốc trên card đồ họa NVIDIA.

---

## 1. Tính Năng Nổi Bật

| Tính năng | Giải pháp công nghệ | Ưu điểm nổi bật |
| :--- | :--- | :--- |
| **Nhận diện Giọng nói (STT)** | **Faster-Whisper (`ctranslate2`)** với mô hình chạy trực tiếp trên GPU/CPU | Nhận diện cực chuẩn, hỗ trợ nhiều mức model từ Tiny đến Large-v3, chạy hoàn toàn offline. |
| **Giọng đọc AI (TTS)** | **Piper TTS Local ONNX** với 6 giọng đọc tiếng Việt: Ban Mai, Chiêu Thanh, Lạc Phi, Mạnh Dũng, Ngọc Huyền, Vais1000 | Tốc độ tổng hợp âm thanh siêu tốc, xử lý 100% trên máy tính, không cần tài khoản hay Internet. |
| **Dịch thuật Thông minh** | Đa chế độ linh hoạt:<br>1. Google Translate Web (miễn phí, không cần key)<br>2. Google Gemini API (`gemini-2.0-flash` văn phong tự nhiên) | Không lo giới hạn dịch thuật, tự động chuyển đổi thông minh khi mạng chậm hoặc mất kết nối. |
| **Quét chữ trên khung hình (OCR)** | **PaddleOCR v4** đa ngôn ngữ | Quét và nhận diện chữ trực tiếp trên video khi âm thanh không rõ. |
| **Tách nhạc & lời (Vocal Separation)** | **Audio-Separator** (BS-Roformer & UVR-MDX-Net) | Tách riêng lời nói gốc và nhạc nền (BGM) để ghép giọng lồng tiếng mới chuẩn xác. |
| **Xử lý & Ghép Video** | **FFmpeg** tích hợp tăng tốc phần cứng NVENC | Xuất video chất lượng cao 1080p Full HD / 60fps nhanh chóng, video xuất ra sạch 100% không dính watermark. |
| **Tải Video Đa Nền Tảng** | **yt-dlp** tích hợp trong tab Tải Video | Hỗ trợ tải video Douyin, TikTok, Bilibili với chất lượng cao nhất. |

---

## 2. Yêu Cầu Phần Cứng & Môi Trường

- **Hệ điều hành:** Windows 10 / Windows 11 (64-bit).
- **Phần cứng tối ưu:**
  - **Card đồ họa (GPU):** NVIDIA GeForce RTX (khuyên dùng RTX 3050 trở lên, VRAM >= 4GB) hỗ trợ CUDA 11.8 / 12.x.
  - **CPU:** Intel Core i5 / AMD Ryzen 5 trở lên.
  - **RAM:** Tối thiểu 8GB (khuyên dùng 16GB).
  - **Ổ cứng:** Còn trống tối thiểu 5GB - 10GB cho các mô hình AI.
- **Phần mềm:**
  - Python 3.10 (64-bit).
  - Toàn bộ thư viện C++/CUDA, DLLs và FFmpeg đã được chuẩn hóa trong thư mục `_internal`.

---

## 3. Hướng Dẫn Khởi Chạy Ứng Dụng

### Cách 1: Khởi chạy nhanh bằng file `.bat` (Khuyên dùng)
Nhấp đúp chuột vào file:
```bat
hikari_dub.bat
```
Script sẽ tự động nạp cấu hình GPU/CPU tối ưu và mở giao diện ứng dụng.

### Cách 2: Khởi chạy bằng dòng lệnh
```powershell
$env:PYTHONIOENCODING="utf-8"
python main.py
```

### Cách 3: Kiểm tra môi trường trước khi chạy
Nhấp đúp chuột vào file:
```bat
check_env.bat
```

---

## 4. Hướng Dẫn Sử Dụng Chi Tiết

### Bước 1: Chọn Video và Thư mục lưu
- Tại tab **Trang chủ**, nhấn **Chọn Video** để nạp một hoặc nhiều video (.mp4, .mkv, .mov).
- Chọn **Thư mục lưu file** xuất ra.

### Bước 2: Bóc Băng Kịch Bản (STT)
- Chọn chế độ bóc băng phù hợp với phần cứng:
  - *Tiny:* Siêu tốc, tốn ít tài nguyên.
  - *Small:* Cân bằng, tối ưu cho GPU 4GB VRAM.
  - *Large-v3:* Độ chuẩn xác cao nhất.
  - *OCR:* Dùng PaddleOCR quét chữ trực tiếp trên video.
- Nhấn **Bóc Băng**.

### Bước 3: Dịch Thuật
- Chọn ngôn ngữ đích (mặc định: **Tiếng Việt**).
- Nhấn **Dịch Kịch Bản**:
  - Tự động dùng hệ thống dịch miễn phí chất lượng cao không giới hạn hoặc sử dụng Gemini API nếu đã cấu hình key.

### Bước 4: Tạo Giọng Đọc Tiếng Việt
- Tại danh sách giọng đọc, chọn giọng đọc mong muốn:
  - `Ban Mai (Nữ)`
  - `Mạnh Dũng (Nam)`
  - `Chiêu Thanh (Nữ)`
  - `Lạc Phi (Nữ)`
  - `Ngọc Huyền (Nữ)`
  - `Vais1000 (Nữ tự nhiên)`
- Nhấn **Tạo Giọng Đọc**.

### Bước 5: Ghép và Xuất Video
- Tùy chỉnh âm lượng nhạc nền (BGM), âm lượng giọng đọc (Voice), phông chữ phụ đề, vị trí và hiệu ứng.
- Nhấn **Render Video**: Video xuất ra sạch 100%, sắc nét Full HD 60fps.

---

## 5. Quản Lý & Tải Mô Hình AI

- **Cách 1 (Trực tiếp trên giao diện):** Vào tab **Cài Đặt** > Nhấn **Tải / Sửa lỗi Tất cả Model**.
- **Cách 2 (Script độc lập):** Nhấp đúp chuột chạy file:
```bat
download_models.bat
```
Mô hình sẽ tự động được tải về lưu trữ cục bộ trong thư mục `models/`.
