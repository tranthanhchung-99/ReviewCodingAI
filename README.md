# 💬 BUG BUSTERS

Ứng dụng **Bug Busters** giúp bạn **phân tích code tự động bằng Azure OpenAI**, hỗ trợ:
- Kiểm tra **coding convention**
- Phân tích **bảo mật**
- Sinh **test case**
- Hỗ trợ **đa ngôn ngữ (Việt/Anh)**
- Nhận diện code trong **ảnh OCR**
- Giao diện đẹp, dễ dùng với **Streamlit**

---

🧠 Tính năng nổi bật

| Tính năng         | Mô tả                                            |
| ----------------- | ------------------------------------------------ |
| 🔍 Review Code    | Phân tích code chi tiết bằng Azure OpenAI        |
| 🧠 Linter         | Tự động chạy flake8 để phát hiện lỗi cú pháp     |
| 🖼️ OCR           | Đọc text từ hình ảnh code (PNG, JPG)             |
| 🌐 Đa ngôn ngữ    | Giao diện Tiếng Việt & English                   |
| 🧪 Sinh Test Case | Tự động tạo test cases hữu ích                   |
| 💬 Chat           | Hỏi AI về lỗi, logic hoặc đề xuất cải thiện code |

---

💻 Hướng dẫn thao tác trên giao diện

🔧 Sidebar

Ngôn ngữ / Language → Chọn Tiếng Việt hoặc English

Upload file → Chọn file .py, .js, .java, .ts, .zip, hoặc ảnh .png/.jpg

Reviewer Mode → Chọn kiểu review:

👨‍🏫 Mentor: Giải thích dễ hiểu

🧠 Senior Dev: Phân tích chuyên sâu

🛡️ Security Expert: Tập trung vào bảo mật

🧹 Style Checker: Kiểm tra format code

Các nút chức năng:

▶️ Bắt đầu Review — Gửi code lên AI để phân tích

🧹 Xóa Chat — Xóa toàn bộ lịch sử chat

🧪 Sinh Test Case — Sinh test case dựa trên code đã review

---

## 🗂️ Cấu trúc thư mục dự án

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

## ⚙️ Hướng dẫn cài môi trường

Run bash
pip install streamlit openai python-dotenv pillow pytesseract flake8 pytest watchdog

## ⚙️ Chạy ứng dụng

Set up tài khoản vào file .env
Run bash
streamlit run BugBusters/src/main.py
