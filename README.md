
# 🐞 BugBusters — AI Code Reviewer

### 🚀 _AI-powered multi-language code review & convention checker_

---

## 🧠 1. Overview

Hiện nay, các lập trình viên thường gặp nhiều vấn đề trong quá trình phát triển phần mềm như:

- Code chưa tuân thủ **coding convention** nội bộ.  
- Xuất hiện **bug tiềm ẩn** hoặc **vấn đề hiệu năng** khó phát hiện thủ công.  
- Cần **review nhanh** code từ nhiều ngôn ngữ khác nhau (Python, Java, C#, C++, JS, TS...).  
- Mất nhiều thời gian **trao đổi giữa reviewer và developer**.

**BugBusters** ra đời với mục tiêu trở thành một **AI Reviewer thông minh**:
- Tự động đọc và phân tích code.
- Phát hiện vi phạm convention, lỗi logic, vấn đề hiệu năng.
- Đưa ra gợi ý sửa chi tiết, có minh họa.
- Cho phép lập trình viên **chat trực tiếp với AI Reviewer** để hỏi thêm về lỗi hoặc best practice.

> 💡 “Tối ưu hóa quy trình review — giúp code tốt hơn, nhanh hơn, sạch hơn.”

---

## ⚙️ 2. Main Features & Use Cases

| **Tính năng chính** | **Mô tả chi tiết** |
|----------------------|--------------------|
| 🧩 **Style Checker** | So sánh code với danh sách rule convention (Excel), highlight rule vi phạm và đề xuất sửa. |
| ⚡ **Performance Checker** | Phân tích logic, phát hiện bug tiềm ẩn và đánh giá hiệu năng từng đoạn code. |
| 🧠 **AI Chat Reviewer** | Giao tiếp trực tiếp với AI để hỏi về lỗi, cách sửa hoặc tư vấn kỹ thuật. |
| 🖼️ **OCR + Vision** | Tự động đọc code từ ảnh, trích xuất nội dung và phát hiện ngôn ngữ code. |
| 🧹 **Linter Integration** | Kết nối flake8, ESLint, g++, javac… để bắt lỗi syntax đa ngôn ngữ. |
| 🧭 **Auto Language Detection** | Phát hiện ngôn ngữ code ngay cả khi không có extension hoặc từ ảnh OCR. |
| 📘 **Convention Flexibility** | Cho phép upload nhiều file rule convention khác nhau (theo từng ngôn ngữ). |
| 🗨️ **Unified Review + Chat** | Giao diện Streamlit kết hợp: hiển thị review & chat tương tác trong cùng một màn hình. |
| 🧠 **Chunk tree sitter** | Tự động chia context theo function với đa dạng ngôn ngữ được hỗ trợ từ thư viện tree sitter. |

---

## 🧩 3. Tech Stack

### 🔸 **Core Framework**
- **Python 3.11+**
- **Streamlit** → giao diện web app chính, trực quan & realtime.

### 🔸 **AI & NLP**
- **Azure OpenAI (GPT-4o / GPT-4o-mini)** → xử lý logic, review code, sinh gợi ý.
- **pytesseract + Pillow** → OCR trích xuất code từ ảnh.
- **Tree-sitter (optional)** → phân tách code theo cấu trúc ngôn ngữ (AST-level chunking).

### 🔸 **Code Analysis**
- **flake8** – lint Python  
- **ESLint** – lint JavaScript/TypeScript  
- **javac, g++, tsc** – kiểm tra syntax cho Java, C++, TS  
- **subprocess** – thực thi lint command động theo ngôn ngữ.

### 🔸 **Data Handling**
- **pandas** – đọc & kiểm tra file convention Excel.  
- **openpyxl** – hỗ trợ Excel backend.

### 🔸 **Environment & Config**
- **dotenv** – quản lý key Azure.  
- **pathlib, tempfile, os** – xử lý file tạm và upload.

### 🔸 **UI & Output Formatting**
- **Markdown + syntax highlight** – hiển thị review đẹp, rõ ràng.  
- **Streamlit Chat Components** – tạo giao diện hội thoại AI như IDE assistant.

---

## 🏗️ 4. Project Structure

```bash
BugBusters/
├── src/
│   ├── main.py                  # entry chính, giao diện streamlit
│   ├── utils/
│   │   ├── utils.py             # toàn bộ logic OCR, AI, lint, rule checking
│   │   ├── LANGUAGES.py         # đa ngôn ngữ giao diện (vi / en)
│   │   ├── chunk_utils.py       # (tùy chọn) phân tách code theo tree-sitter
│   └── __init__.py
│
├── tests/
│   ├── sample_code_python.py
│   ├── sample_code_java.java
│   ├── sample_code_csharp.cs
│   ├── rule_convention_full.xlsx
│   └── rule_convention_missing.xlsx
│
├── .env                         # chứa AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY
├── requirements.txt              # danh sách thư viện
├── README.md
└── run.sh / run.bat             # script khởi chạy nhanh (tuỳ OS)
```

---

## 💻 5. Installation & Setup Guide

### 🧰 **1. Clone source**
```bash
git clone https://github.com/yourname/BugBusters.git
cd BugBusters
```

### 🧱 **2. Tạo virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate       # Linux / macOS
.venv\Scripts\activate        # Windows
```

### 📦 **3. Cài thư viện**
```bash
pip install -r requirements.txt
```

### 🔑 **4. Cấu hình Azure API**
Tạo file `.env` ở thư mục gốc:
```env
AZURE_OPENAI_ENDPOINT=https://<your-endpoint>.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-key>
```

### ▶️ **5. Chạy ứng dụng**
```bash
cd src
streamlit run main.py
```

---

## 🧪 6. Testing
Thư mục `tests/` chứa:
- `sample_code_python.py`, `sample_code_java.java`, `sample_code_csharp.cs`  
  → Dùng để kiểm thử logic nhận dạng ngôn ngữ & lint syntax.  
- `rule_convention_full.xlsx` và `rule_convention_missing.xlsx`  
  → Dùng để kiểm thử chức năng đọc rule đầy đủ hoặc thiếu cột.

---

## 🧭 7. Future Improvements
- Hỗ trợ review theo **custom prompt template**.  
- Lưu lịch sử review và export báo cáo PDF.  
- Hỗ trợ thêm ngôn ngữ mới: PHP, Go, Rust.  
- Nâng cấp UI sang **React-based dashboard** cho enterprise team.

---

## ❤️ Credits
- **Author:** Bạn và AI Reviewer (GPT-5)  
- **Tech:** Python, Streamlit, Azure OpenAI  
- **Version:** v2.5 Stable (Nov 2025)
