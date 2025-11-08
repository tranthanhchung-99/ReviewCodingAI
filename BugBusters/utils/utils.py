import os
import re
import subprocess
import pytesseract
import pandas as pd
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

MODEL = "gpt-4o-mini"

# =========================================
# CHUNK TEXT / CODE
# =========================================
def _chunk_fallback(text: str, chunk_size: int = 3000):
    """Fallback chia text nếu không dùng tree-sitter."""
    text = text or ""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

try:
    from utils.chunk_utils import chunk_text as _chunk_by_language

    def chunk_text(text: str, ext: str = ".py", max_chunk_size: int = 3000):
        """Chia code theo ngôn ngữ bằng tree-sitter."""
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
    """Đọc file text an toàn."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1") as f:
            return f.read()
    except Exception as e:
        return f"⚠️ Lỗi khi đọc file {file_path}: {e}"

# =========================================
# LANGUAGE DETECTION
# =========================================
def detect_language(file_name: str, content: str = "") -> str:
    """Phát hiện ngôn ngữ từ file extension hoặc nội dung."""
    ext = os.path.splitext(file_name)[1].lower()
    ext_map = {
        ".py": "python", ".js": "javascript", ".ts": "typescript",
        ".cpp": "cpp", ".c": "c", ".java": "java",
        ".cs": "csharp", ".go": "go", ".php": "php"
    }
    if ext in ext_map:
        return ext_map[ext]

    # fallback: dựa theo nội dung
    if "def " in content or "import " in content:
        return "python"
    if "function " in content or "const " in content:
        return "javascript"
    if "#include" in content:
        return "cpp"
    if "class " in content and "public static void main" in content:
        return "java"

    return "unknown"

# =========================================
# SHELL COMMANDS & LINTERS
# =========================================
def run_command(command: str, cwd: str = None):
    """Chạy lệnh shell và trả kết quả."""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd,
                                capture_output=True, text=True)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return -1, "", str(e)

def lint_code(file_path: str, language: str):
    """Kiểm tra syntax bằng công cụ tương ứng — trả về (exit_code, stdout, stderr)."""
    language = language.lower()
    if language == "python":
        return run_command(f"flake8 \"{file_path}\"")
    elif language == "javascript":
        return run_command(f"eslint \"{file_path}\" --no-color")
    elif language == "typescript":
        return run_command(f"tsc --noEmit \"{file_path}\"")
    elif language == "cpp":
        return run_command(f"g++ -fsyntax-only \"{file_path}\"")
    elif language == "java":
        return run_command(f"javac \"{file_path}\"")
    else:
        return -1, "", f"Không có linter cho ngôn ngữ: {language}"

# =========================================
# LLM CALL
# =========================================
def summarize_with_llm(messages: list[dict]) -> str:
    """Gửi prompt đến LLM."""
    try:
        response = client.chat.completions.create(
            model=MODEL, messages=messages, temperature=0.3, max_tokens=2000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Lỗi khi gọi LLM: {e}"

# =========================================
# CONVENTION CHECKER
# =========================================
def load_convention_file(uploaded_file):
    """
    Đọc file convention Excel và đảm bảo có đủ cột cần thiết.
    Nếu thiếu cột -> tự thêm cột trống + log cảnh báo.
    """
    required_cols = ["Rule", "Description", "Severity", "Example", "Suggestion", "Pattern"]
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = [str(c).strip() for c in df.columns]

        # Bổ sung cột bị thiếu
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            print(f"⚠️ File convention thiếu cột: {missing}. Hệ thống sẽ tự thêm cột trống.")
            for col in missing:
                df[col] = ""

        # Giữ đúng thứ tự cột
        df = df[[c for c in required_cols if c in df.columns]]

        # Chuyển thành list[dict]
        rules = df.to_dict(orient="records")
        print(f"✅ Đã đọc {len(rules)} rule từ file convention.")
        return rules

    except Exception as e:
        print(f"⚠️ Lỗi khi đọc file convention: {e}")
        return []

def check_code_style_against_rules(code: str, rules: list[dict]):
    """
    So sánh code với rule convention.
    Nếu thiếu Pattern thì bỏ qua rule đó để không lỗi.
    """
    results = []
    for rule in rules:
        pattern = rule.get("Pattern", "").strip()
        if not pattern:
            print(f"⚠️ Bỏ qua rule thiếu Pattern: {rule.get('Rule', 'Unnamed Rule')}")
            continue

        try:
            if re.search(pattern, code, re.MULTILINE):
                results.append({
                    "Rule": rule.get("Rule", "No Name"),
                    "Description": rule.get("Description", ""),
                    "Severity": rule.get("Severity", "Medium"),
                    "Example": rule.get("Example", ""),
                    "Suggestion": rule.get("Suggestion", ""),
                    "Violated": True
                })
        except re.error as e:
            results.append({
                "Rule": rule.get("Rule", "Regex Error"),
                "Description": f"Lỗi regex: {e}",
                "Severity": "Error",
                "Example": "",
                "Suggestion": "",
                "Violated": True
            })
    return results

# =========================================
# OCR & VISION
# =========================================
def extract_text_from_image(uploaded_image):
    """Trích text từ ảnh bằng pytesseract."""
    try:
        image = Image.open(uploaded_image)
        text = pytesseract.image_to_string(image, lang="eng+vie")
        return text.strip()
    except Exception as e:
        return f"⚠️ Lỗi OCR: {e}"

def analyze_image_with_llm(image_path):
    """Phân tích ảnh bằng model vision (nếu có code thì trích ra)."""
    try:
        from base64 import b64encode

        with open(image_path, "rb") as f:
            img_base64 = b64encode(f.read()).decode("utf-8")

        messages = [
            {"role": "system", "content": (
                "Bạn là chuyên gia phân tích hình ảnh UI và code. "
                "Nếu ảnh chứa code, trích xuất code chính xác ra text.")},
            {"role": "user", "content": [
                {"type": "text", "text": "Phân tích ảnh này và trích xuất code (nếu có):"},
                {"type": "image_url", "image_url": f"data:image/png;base64,{img_base64}"}
            ]}
        ]

        response = client.chat.completions.create(
            model=MODEL, messages=messages, temperature=0.3, max_tokens=2000
        )

        content = response.choices[0].message.content.strip()
        if "```" in content:
            code_blocks = re.findall(r"```[a-zA-Z0-9]*\n([\s\S]*?)```", content)
            if code_blocks:
                return "\n".join(code_blocks).strip()
        return content
    except Exception as e:
        return f"⚠️ Lỗi khi phân tích ảnh: {e}"
