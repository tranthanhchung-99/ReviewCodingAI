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

client = OpenAI(
    base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)
MODEL = "gpt-4o-mini"  # hoặc model vision mà server của bạn hỗ trợ

# =========================================
# CHUNK TEXT / CODE
# =========================================
def _chunk_fallback(text: str, chunk_size: int = 3000):
    """Fallback chia text theo độ dài nếu không có tree-sitter."""
    text = text or ""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

try:
    from utils.chunk_utils import chunk_text as _chunk_by_language

    def chunk_text(text: str, ext: str = ".py", max_chunk_size: int = 3000):
        """Chia code theo ngôn ngữ nếu có tree-sitter; fallback nếu lỗi."""
        try:
            return _chunk_by_language(text, ext, max_chunk_size)
        except Exception as e:
            print(f"⚠️ Tree-sitter lỗi ({ext}): {e} → fallback chia thô.")
            return _chunk_fallback(text, max_chunk_size)
except ImportError:
    def chunk_text(text: str, ext: str = ".py", max_chunk_size: int = 3000):
        return _chunk_fallback(text, max_chunk_size)


# =========================================
# FILE HANDLING
# =========================================
def safe_read_text(file_path: str) -> str:
    """Đọc nội dung file text (utf-8, fallback latin-1)."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1") as f:
            return f.read()
    except Exception as e:
        return f"⚠️ Lỗi khi đọc file {file_path}: {e}"


# =========================================
# SHELL COMMANDS
# =========================================
def run_command(command: str, cwd: str = None):
    """Chạy một lệnh hệ thống và trả về (exit_code, stdout, stderr)."""
    try:
        result = subprocess.run(
            command, shell=True, cwd=cwd,
            capture_output=True, text=True
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)


# =========================================
# LLM CALL (STU Proxy / OpenAI API)
# =========================================
def summarize_with_llm(messages: list[dict]):
    """Gửi danh sách messages đến LLM qua proxy hoặc Azure."""
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
# OCR (TỪ ẢNH)
# =========================================
def extract_text_from_image(uploaded_image):
    """Trích xuất text từ ảnh bằng pytesseract (Eng + Vie)."""
    try:
        image = Image.open(uploaded_image)
        text = pytesseract.image_to_string(image, lang="eng+vie")
        return text.strip()
    except Exception as e:
        return f"⚠️ Lỗi OCR: {e}"


# =========================================
# PHÂN TÍCH ẢNH BẰNG AI (VISION)
# =========================================
def analyze_image_with_llm(image_path):
    """
    Phân tích ảnh bằng model có vision:
    - Mô tả nội dung ảnh
    - Nếu phát hiện code, trích ra code text
    """
    try:
        from base64 import b64encode

        with open(image_path, "rb") as f:
            img_base64 = b64encode(f.read()).decode("utf-8")

        messages = [
            {
                "role": "system",
                "content": (
                    "Bạn là chuyên gia phân tích hình ảnh phần mềm, UI và code. "
                    "Nếu trong ảnh có đoạn code (dù là ảnh chụp màn hình), "
                    "hãy trích xuất chính xác đoạn code đó ra text. "
                    "Nếu không có code, chỉ cần mô tả nội dung ảnh."
                )
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Phân tích và trích xuất code từ ảnh này nếu có:"},
                    {"type": "image_url", "image_url": f"data:image/png;base64,{img_base64}"}
                ]
            }
        ]

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # hoặc model vision khác
            messages=messages,
            temperature=0.3,
            max_tokens=2000
        )

        ai_result = response.choices[0].message.content.strip()

        # ✅ Nếu AI phát hiện đoạn code, tách riêng ra cho dễ dùng
        if "```" in ai_result:
            import re
            code_blocks = re.findall(r"```[a-zA-Z0-9]*\n([\s\S]*?)```", ai_result)
            if code_blocks:
                code_text = "\n\n".join(code_blocks).strip()
                return f"### 🧠 AI nhận diện code từ ảnh:\n```{code_text}```"
        return f"### 🧠 Phân tích ảnh:\n{ai_result}"

    except Exception as e:
        return f"⚠️ Lỗi khi phân tích ảnh bằng AI: {e}"
