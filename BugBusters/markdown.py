# Tổng quan Bug Busters

## 1. Tính năng chính

- **Review code tự động** bằng Azure OpenAI (GPT-4o mini), hỗ trợ đa ngôn ngữ (Việt/Anh)
- **Kiểm tra convention, style, phân tích bảo mật** với nhiều reviewer mode:
    - Mentor (giải thích dễ hiểu)
    - Senior Dev (phân tích chuyên sâu)
    - Security Expert (bảo mật)
    - Style Checker (format code)
- **Sinh test case tự động** cho code vừa review (bao gồm cả edge case)
- **OCR ảnh**: Nhận diện và review code từ hình ảnh (png, jpg)
- **Chat trực tiếp với AI** về code, lỗi, gợi ý fix, giải thích, v.v.
- **Upload nhiều loại file**: .py, .js, .java, .ts, ZIP, PNG, JPG
- **Quản lý lịch sử chat, review, test case** trong phiên làm việc
- **Hiển thị code với syntax highlight và so sánh trước/sau khi AI refactor** (nếu có)
- **Giới hạn và cảnh báo file lớn**, chia nhỏ và review từng phần code
- **Tải về test case** dưới dạng file `.json`

---

## 2. Công cụ & Thư viện hỗ trợ

- **Streamlit**: Giao diện web, quản lý session, tương tác real-time
- **Azure OpenAI**: Model GPT-4o mini cho phân tích, review, sinh test case, dịch thuật
- **python-dotenv**: Quản lý thông tin endpoint/API key bảo mật qua file `.env`
- **Pillow, pytesseract**: Xử lý ảnh, nhận diện text từ file PNG/JPG (OCR)
- **Subprocess**: Chạy linter (flake8 cho Python) để kiểm tra code
- **zipfile, pathlib, tempfile**: Xử lý ZIP, quản lý file tạm, đọc file các ngôn ngữ
- **Custom đa ngôn ngữ**: Module `LANGUAGES.py` cho giao diện tiếng Việt/Anh

---

## 3. Flow màn hình & thao tác

### **Sidebar**
- **Chọn ngôn ngữ:** Tiếng Việt hoặc English
- **Upload file:** Code (.py, .js, .java, .ts), ZIP, ảnh PNG/JPG
- **Reviewer Mode:** Chọn kiểu review (Mentor, Senior Dev, Security Expert, Style Checker)
- **Bắt đầu Review:** Gửi code/tài liệu lên AI để phân tích & nhận kết quả
- **Xóa Chat:** Reset lịch sử chat và review
- **Sinh Test Case:** Sau khi review, nhấn để AI sinh bộ test case cho code

### **Tab Chat**
- Hiển thị lịch sử chat giữa bạn và AI
- Nhập câu hỏi yêu cầu giải thích, fix lỗi, phân tích, v.v. về code vừa review

### **Tab Test Cases**
- Hiển thị test case đã sinh ra cho code
- Tải về file `.json` test case để sử dụng

### **Kết quả Review**
- Tóm tắt kết quả review cho từng file
- Danh sách lỗi/gợi ý, có thể mở rộng xem chi tiết từng lỗi
- Nếu AI gợi ý code đã refactor/sửa, hiển thị song song code gốc và code đề xuất

---

## 4. Cấu trúc thư mục dự án
REVIEWCODINGAI/
└── BugBusters/
├── src/
│ ├── init.py
│ └── main.py # File chạy chính, giao diện Streamlit
├── utils/
│ ├── init.py
│ ├── utils.py # Hàm tiện ích xử lý code, OCR, gọi OpenAI
│ └── LANGUAGES.py # Module đa ngôn ngữ cho giao diện
├── .env # Thông tin API key và endpoint Azure OpenAI
├── markdown.py # (Tuỳ chọn) module xử lý Markdown nếu có
└── setup_env.txt # File ghi chú môi trường cài đặt
└── README.md

---

## 5. Tóm tắt workflow xử lý

1. **Người dùng upload file/code/ảnh** → Chọn reviewer mode → Bấm "Bắt đầu Review"
2. **Hệ thống xử lý file:** Đọc nội dung, chạy linter (nếu là Python), chia nhỏ code nếu quá lớn
3. **Gửi prompt lên Azure OpenAI** theo reviewer mode → Nhận kết quả review (tóm tắt, lỗi, gợi ý, code đề xuất)
4. **Hiển thị kết quả review trên UI:** Tóm tắt, lỗi, code so sánh, lưu lịch sử chat
5. **Người dùng có thể chat hỏi AI** về code, lỗi, cách fix, giải thích sâu hơn
6. **Sau khi review, có thể sinh test case** cho code vừa review, tải test case về

---

## 6. Lưu ý bảo mật & sử dụng

- Không upload file chứa thông tin nhạy cảm hoặc bí mật lên AI nếu chưa kiểm soát bảo mật
- Bảo mật file `.env` (API Key), không chia sẻ lên GitHub/public
- Nếu chạy trên server/cloud, nên cấu hình xác thực và giới hạn quyền truy cập

---

## 7. Troubleshooting

- Lỗi OCR: Kiểm tra đã cài đúng Tesseract OCR, bổ sung đường dẫn vào PATH nếu cần
- Lỗi API: Kiểm tra endpoint/API Key trong `.env`, tài khoản Azure OpenAI còn quota và quyền sử dụng model
- Lỗi file upload: Chỉ upload file <100,000 ký tự, đúng định dạng hỗ trợ; file lớn sẽ chỉ review phần đầu

---

## 8. Liên hệ & Đóng góp

Nếu có vấn đề hoặc muốn đóng góp, hãy liên hệ hoặc tạo issue tại repo của bạn.

---