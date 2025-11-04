# 💬 BUG BUSTERS

**Bug Busters** là ứng dụng AI giúp bạn **phân tích và review code tự động** bằng **Azure OpenAI**, hỗ trợ đa ngôn ngữ lập trình, kiểm tra coding convention, đánh giá hiệu năng và nhận diện code từ ảnh.

---

## 🌟 Tính năng nổi bật

| Tính năng                 | Mô tả                                                                 |
| -------------------------- | --------------------------------------------------------------------- |
| 🔍 Review Code             | Phân tích chi tiết từng file code, tách đoạn, gợi ý sửa lỗi cụ thể   |
| ⚙️ Reviewer Mode            | 2 chế độ chuyên biệt: **Style Checker** và **Performance Expert**    |
| 📘 Coding Convention        | Tải file Excel quy tắc coding convention riêng cho từng dự án        |
| 🧠 Linter (flake8)          | Phát hiện lỗi cú pháp Python và cảnh báo format code                 |
| 🖼️ OCR                    | Nhận diện code từ hình ảnh (.png, .jpg)                              |
| 🌐 Đa ngôn ngữ giao diện     | Tiếng Việt 🇻🇳 & English 🇬🇧                                         |
| 💬 Chat cùng AI             | Đặt câu hỏi, nhận lời khuyên và cải thiện code                       |

---

## 💻 Ngôn ngữ được hỗ trợ review

Bug Busters có thể **nhận diện và review hơn 20 ngôn ngữ phổ biến**, bao gồm:

| Nhóm | Ngôn ngữ được hỗ trợ |
|------|----------------------|
| 🐍 Backend | Python (.py), Java (.java), C (.c), C++ (.cpp), C# (.cs), Go (.go), Rust (.rs), PHP (.php) |
| 🌐 Frontend | JavaScript (.js), TypeScript (.ts), HTML (.html), CSS (.css) |
| ⚙️ Scripting | Bash (.sh), Lua (.lua), Ruby (.rb), SQL (.sql), Markdown (.md), YAML (.yaml), TOML (.toml) |
| 📱 Mobile & Others | Swift (.swift), Kotlin (.kt), Scala (.scala), Dart (.dart) |

> 🧩 Ứng dụng tự động nhận diện extension file để áp dụng **Tree-sitter** phân tích cú pháp chính xác cho từng ngôn ngữ.

---

## 📘 File Coding Convention (Excel)

Tải lên 1 file `.xlsx` chứa danh sách quy tắc convention của dự án.  
Mỗi quy tắc nên có cấu trúc như sau:

| Rule | Description | Keyword |
|------|--------------|----------|
| PEP8 | Tên biến phải dùng snake_case | snake_case |
| Magic Number | Không dùng số cứng trong code | 42 |
| Function Length | Hàm không quá 50 dòng | def |

> ⚠️ **Keyword** giúp AI phát hiện đoạn code nào có thể vi phạm quy tắc tương ứng.  
> AI sẽ **đối chiếu cả Coding Convention + Linter + Logic** để đưa ra đánh giá cuối cùng.

---

## 🧭 Hướng dẫn thao tác giao diện

### 🔧 **1. Sidebar (Cài đặt)**

| Mục | Mô tả |
|-----|-------|
| 🌐 **Ngôn ngữ / Language** | Chọn Tiếng Việt 🇻🇳 hoặc English 🇬🇧 |
| 📂 **Upload File** | Chọn file code (.py, .js, .java, .ts, .zip) hoặc ảnh (.png/.jpg) |
| 📘 **Upload Convention File** | Tải file Excel quy tắc Coding Convention |
| ⚙️ **Reviewer Mode** | Chọn chế độ phân tích: `Style Checker` hoặc `Performance Expert` |
| ▶️ **Bắt đầu Review** | Gửi code + convention lên AI để phân tích |
| 🧹 **Xóa Chat** | Xóa lịch sử chat và kết quả review cũ |

---

### 🎯 **2. Reviewer Mode – Hai chế độ chuyên biệt**

#### 🧹 **Style Checker**
- Kiểm tra **coding convention**, **format**, **naming convention**, **comment**, **PEP8**, v.v.
- So sánh với **file convention Excel** mà bạn tải lên.
- Đưa ra:
  - Các quy tắc bị vi phạm (dưới dạng bảng)
  - Gợi ý **đoạn code đã chỉnh sửa đúng convention**
  - Giải thích ngắn gọn lý do

#### ⚡ **Performance Expert**
- Phân tích **logic, hiệu năng, bảo mật, và maintainability**.
- Đưa ra nhận định chi tiết từng đoạn code:
  - Điểm yếu về cấu trúc
  - Nút thắt hiệu năng (vòng lặp, I/O, DB query, recursion, v.v.)
  - Gợi ý refactor hoặc tối ưu
- Tập trung nhiều hơn vào chất lượng tổng thể thay vì format.

---

### 💬 **3. Chat với AI Reviewer**

Sau khi review, bạn có thể:
- Đặt câu hỏi cụ thể như:  
  > "Tại sao đoạn này bị vi phạm convention?"  
  > "Có cách nào tối ưu hàm này không?"  
- AI sẽ trả lời dựa trên **ngữ cảnh từ kết quả review trước đó**.

---

## 🗂️ Cấu trúc thư mục dự án

REVIEWCODINGAI/
└── BugBusters/
├── src/
│ └── main.py # Giao diện chính (Streamlit)
├── utils/
│ ├── utils.py # OCR, OpenAI call, xử lý text/code
│ ├── chunk_utils.py # Tree-sitter chia code thông minh
│ ├── convention_util.py # Đọc & quản lý file coding convention
│ └── LANGUAGES.py # Đa ngôn ngữ giao diện
├── .env # Chứa API key & endpoint Azure OpenAI
├── setup_env.txt # Thư viện cần cài
└── README.md

---

## ⚙️ Cài đặt môi trường

```bash
pip install -r setup_env.txt


---

## 🚀 Chạy ứng dụng
streamlit run BugBusters/src/main.py
