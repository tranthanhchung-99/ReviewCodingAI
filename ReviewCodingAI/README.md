# 💬 AI Code Reviewer

Ứng dụng AI hỗ trợ **review code, phân tích lỗi, bảo mật, và sinh test case tự động** — được xây dựng bằng **Streamlit** và **Azure OpenAI (GPT-4o-mini)**.

---

## 🚀 Demo nhanh

![screenshot](https://cdn-icons-png.flaticon.com/512/4712/4712038.png)

---

## 🧭 Cài đặt

### 1️⃣ Clone và tạo môi trường

```bash
cd ReviewCoddingAI
python -m venv .venv
source .venv/bin/activate   # hoặc .venv\Scripts\activate trên Windows
```

### 2️⃣ Cài thư viện

```bash
pip install -r setup_env.txt
```

### 3️⃣ Tạo file `.env`

```bash
AZURE_OPENAI_ENDPOINT=https://<your-resource-name>.openai.azure.com/
AZURE_OPENAI_API_KEY=<your-azure-api-key>
```

### 4️⃣ Chạy ứng dụng

```bash
streamlit run app.py
```

Mở [http://localhost:8501](http://localhost:8501) trong trình duyệt.

---

## 🧠 Tính năng chính

| Tính năng             | Mô tả                                                            |
| --------------------- | ---------------------------------------------------------------- |
| 🧑‍💻 **Code Review**    | Phân tích và đánh giá code theo tiêu chí kỹ thuật hoặc bảo mật   |
| 🧪 **Sinh Test Case** | Tự động sinh test case JSON cho code                             |
| 📷 **OCR từ ảnh**     | Hỗ trợ đọc code từ ảnh qua Tesseract OCR                         |
| 💬 **Chat trực tiếp** | Hỏi AI về cách fix lỗi hoặc tối ưu code                          |
| ⚙️ **Reviewer Mode**  | Nhiều phong cách review: Mentor, Senior, Security, Style Checker |

---

## 📦 Thư viện chính

- [Streamlit](https://streamlit.io/)
- [Azure OpenAI](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Pillow](https://pillow.readthedocs.io/)
- [pytesseract](https://pypi.org/project/pytesseract/)
- [flake8](https://flake8.pycqa.org/)

---

## 🧩 Cấu trúc thư mục

```
ReviewCodingAI/
├── app.py
├── setup_env.txt
├── .env
└── README.md
```

---

---

## 👨‍💻 Tác giả

**TEAM: Bug Busters**
