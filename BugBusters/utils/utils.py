import os
import subprocess
import pytesseract
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image

# =========================================
# CONFIG
# =========================================
load_dotenv()

# ⚙️ Cấu hình client cho STU Platform proxy
# Sử dụng base_url thay vì azure_endpoint
client = OpenAI(
    base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)

MODEL = "gpt-4o-mini"  # hoặc đổi thành model mà STU server hỗ trợ

# =========================================
# HÀM CHIA NHỎ TEXT (để gửi lên LLM)
# =========================================
def chunk_text(text: str, chunk_size: int = 3000):
    """Chia nhỏ đoạn văn bản để xử lý với LLM."""
    text = text or ""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# =========================================
# HÀM ĐỌC FILE AN TOÀN
# =========================================
def safe_read_text(file_path):
    """Đọc nội dung text từ file (utf-8, fallback latin-1)."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1") as f:
            return f.read()
    except Exception as e:
        return f"⚠️ Lỗi khi đọc file {file_path}: {e}"

# =========================================
# HÀM CHẠY LỆNH HỆ THỐNG
# =========================================
def run_command(command, cwd=None):
    """Chạy một lệnh shell (ví dụ: flake8) và trả về (exit_code, stdout, stderr)."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

# =========================================
# GỌI LLM (STU Platform Proxy / OpenAI API)
# =========================================
def summarize_with_llm(messages):
    """
    Gửi danh sách messages (list of dict) đến proxy STU Platform,
    trả về nội dung phản hồi dạng string.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Lỗi khi gọi LLM: {e}"

# =========================================
# TRÍCH XUẤT TEXT TỪ ẢNH (OCR)
# =========================================
def extract_text_from_image(uploaded_image):
    """Dùng OCR để trích xuất text từ ảnh."""
    try:
        image = Image.open(uploaded_image)
        text = pytesseract.image_to_string(image, lang="eng+vie")
        return text.strip()
    except Exception as e:
        return f"⚠️ Lỗi OCR: {e}"
