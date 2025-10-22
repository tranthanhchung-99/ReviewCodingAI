import subprocess
from pathlib import Path
from PIL import Image
import pytesseract
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# =========================
# Đọc file text an toàn
# =========================
def safe_read_text(path: Path):
    """
    Đọc file text an toàn, tránh crash khi gặp ký tự lỗi.
    """
    return path.read_text(encoding="utf-8", errors="ignore")


# =========================
# Chia nhỏ text cho mô hình AI
# =========================
def chunk_text(text, max_len=3000):
    """
    Chia nhỏ chuỗi text thành nhiều đoạn nhỏ để gửi lên model.
    """
    return [text[i:i + max_len] for i in range(0, len(text), max_len)]


# =========================
# Chạy lệnh hệ thống (ví dụ flake8)
# =========================
def run_command(cmd, cwd=None, timeout=20):
    """
    Chạy lệnh hệ thống, trả về (exit_code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


# =========================
# Gọi Azure OpenAI (GPT)
# =========================
def summarize_with_llm(messages):
    """
    Gửi danh sách message đến Azure OpenAI và nhận phản hồi.
    """
    load_dotenv()
    client = AzureOpenAI(
        api_version="2024-07-01-preview",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    )
    MODEL = "gpt-4o-mini"
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=800,
            temperature=0.0,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[ERROR calling Azure OpenAI]: {e}"


# =========================
# OCR: Trích xuất text từ ảnh
# =========================
def extract_text_from_image(img_file):
    """
    Dùng pytesseract để đọc text từ ảnh (PNG, JPG, JPEG...).
    """
    img = Image.open(img_file)
    return pytesseract.image_to_string(img, lang="eng")
