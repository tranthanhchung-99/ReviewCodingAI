import os, subprocess
import pytesseract
from openai import AzureOpenAI
from dotenv import load_dotenv
from PIL import Image

load_dotenv()
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01"
)
MODEL = "gpt-4o-mini"

# =========================
# CHUNK CODE
# =========================
def chunk_text(text: str, ext: str = ".py", max_chunk_size: int = 3000):
    """Chia code thành các đoạn nhỏ hợp lý"""
    text = text or ""
    chunks = []
    for i in range(0, len(text), max_chunk_size):
        chunks.append(text[i:i + max_chunk_size])
    return chunks

# =========================
# SAFE FILE READ
# =========================
def safe_read_text(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1") as f:
            return f.read()
    except Exception as e:
        return f"⚠️ Lỗi đọc file {file_path}: {e}"

# =========================
# RUN SHELL
# =========================
def run_command(command: str, cwd: str = None):
    try:
        res = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        return res.returncode, res.stdout, res.stderr
    except Exception as e:
        return -1, "", str(e)

# =========================
# LLM CALL
# =========================
def summarize_with_llm(messages: list[dict]):
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

# =========================
# OCR
# =========================
def extract_text_from_image(image_file):
    try:
        img = Image.open(image_file)
        text = pytesseract.image_to_string(img, lang="eng+vie")
        return text.strip()
    except Exception as e:
        return f"⚠️ Lỗi OCR: {e}"

# =========================
# IMAGE ANALYSIS
# =========================
def analyze_image_with_llm(image_path):
    try:
        from base64 import b64encode
        with open(image_path, "rb") as f:
            img64 = b64encode(f.read()).decode("utf-8")
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Bạn là chuyên gia nhận diện code trong ảnh."},
                {"role": "user", "content": [
                    {"type": "text", "text": "Phân tích nội dung ảnh sau, trích xuất code nếu có:"},
                    {"type": "image_url", "image_url": f"data:image/png;base64,{img64}"}
                ]}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Lỗi khi phân tích ảnh: {e}"
