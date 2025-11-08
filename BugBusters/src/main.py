import sys
import os
import tempfile
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from openai import AzureOpenAI

# === FIX IMPORT PATH ===
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# === IMPORT UTILS ===
from utils.utils import (
    safe_read_text,
    chunk_text,
    summarize_with_llm,
    detect_language,
    lint_code,
    extract_text_from_image,
    analyze_image_with_llm,
    load_convention_file,
    check_code_style_against_rules
)
from utils.LANGUAGES import LANGUAGES

# === CONFIG ===
load_dotenv()
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01"
)
MODEL = "gpt-4o-mini"
MAX_FILE_SIZE = 100_000

st.set_page_config(page_title="💬 Bug Busters", layout="wide")

# === LANGUAGE ===
lang_code = st.sidebar.selectbox("Ngôn ngữ / Language", ["vi", "en"])
T = LANGUAGES[lang_code]

# === SESSION STATE ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "review_results" not in st.session_state:
    st.session_state.review_results = []

# === SIDEBAR ===
st.sidebar.header("⚙️ Settings")
# Dùng dynamic key để ép reset uploader
if "uploader_version" not in st.session_state:
    st.session_state.uploader_version = 0

uploaded_file = st.sidebar.file_uploader(
    T["upload_label"],
    type=["py", "js", "java", "cpp", "ts", "png", "jpg", "jpeg"],
    key=f"code_uploader_{st.session_state.uploader_version}"
)

uploaded_convention = st.sidebar.file_uploader(
    "📘 Upload Coding Convention (Excel)",
    type=["xlsx"],
    key=f"rule_uploader_{st.session_state.uploader_version}"
)

review_mode = st.sidebar.selectbox("🔍 Reviewer Mode", ["Style Checker", "Performance Expert"])
run_btn = st.sidebar.button(T["run_btn"])
clear_btn = st.sidebar.button(T["clear_btn"])

# === CLEAR CHAT ===
# === CLEAR CHAT ===
if clear_btn:
    import shutil
    import tempfile

    # 1️⃣ Xóa toàn bộ session state liên quan
    for key in list(st.session_state.keys()):
        if key not in ["uploader_version"]:  # giữ lại version
            del st.session_state[key]

    # 2️⃣ Dọn file tạm
    temp_dir = tempfile.gettempdir()
    for f in os.listdir(temp_dir):
        path = os.path.join(temp_dir, f)
        try:
            if (f.startswith("tmp") or "bugbusters" in f.lower()):
                if os.path.isdir(path):
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    os.remove(path)
        except Exception as e:
            print(f"⚠️ Không thể xóa {path}: {e}")

    # 3️⃣ Reset uploader bằng cách tăng version
    st.session_state.uploader_version += 1

    st.success("✅ Đã xóa toàn bộ dữ liệu và file upload.")
    st.rerun()

# === SINGLE PAGE: REVIEW + CHAT ===
st.title("🐞 Bug Busters")

# === HIỂN THỊ KẾT QUẢ REVIEW ===
if not st.session_state.review_results:
    st.info(T["requirement_suggestion"])
else:
    for file_result in st.session_state.review_results:
        st.markdown(f"## 📄 File: `{file_result['file']}`")
        for section in file_result["review"]:
            st.markdown(section, unsafe_allow_html=True)

st.markdown("---")

# CSS để khống chế khung chat luôn gọn đẹp và input ở cuối
st.markdown("""
    <style>
    [data-testid="stChatMessage"] {
        max-height: 65vh;
        overflow-y: auto;
    }
    div[data-testid="stChatInput"] {
        position: sticky;
        bottom: 0;
        background-color: white;
        padding-top: 0.5rem;
        border-top: 1px solid #eee;
    }
    </style>
""", unsafe_allow_html=True)

# Hiển thị các tin nhắn trong lịch sử
for msg in st.session_state.chat_history:
    avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Ô nhập chat — luôn nằm cuối, cố định
user_message = st.chat_input(T["enter_chat"])

if user_message:
    # Thêm tin nhắn người dùng
    st.session_state.chat_history.append({"role": "user", "content": user_message})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_message)

    # Gọi AI phản hồi
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🤔 AI đang suy nghĩ..."):
            reply = summarize_with_llm([
                {"role": "system", "content": "Bạn là AI reviewer hỗ trợ phân tích code và gợi ý tối ưu."},
                {"role": "user", "content": user_message}
            ])
            st.markdown(reply)

    # Lưu phản hồi vào session
    st.session_state.chat_history.append({"role": "assistant", "content": reply})

    # Auto scroll xuống cuối
    import streamlit.components.v1 as components
    components.html("""
        <script>
        setTimeout(function() {
            const chatElems = window.parent.document.querySelectorAll('[data-testid="stChatMessageContent"]');
            if (chatElems.length > 0) {
                chatElems[chatElems.length - 1].scrollIntoView({behavior: "smooth", block: "end"});
            }
        }, 400);
        </script>
    """, height=0)

# === REVIEW HANDLER ===
if run_btn and uploaded_file:
    with st.spinner("🚀 Đang phân tích file..."):
        tmp_dir = Path(tempfile.mkdtemp(prefix="bugbusters-"))
        temp_path = tmp_dir / uploaded_file.name
        temp_path.write_bytes(uploaded_file.read())

        # 1️⃣ Đọc nội dung code hoặc OCR ảnh
        if uploaded_file.type.startswith("image/"):
            ocr_text = extract_text_from_image(uploaded_file)
            detected_lang = detect_language(ocr_text)
            st.info(f"🧩 Đã nhận diện ngôn ngữ code: **{detected_lang}**")
            code_content = ocr_text
        else:
            code_content = safe_read_text(temp_path)
            detected_lang = detect_language(code_content)
            st.info(f"🧩 Phát hiện ngôn ngữ: **{detected_lang}**")

        # 2️⃣ Lint code (flake8, eslint, javac...)
        lint_exit, lint_out, lint_err = lint_code(temp_path, detected_lang)

        if lint_out.strip() or lint_err.strip():
            st.markdown("### 🧾 Linter Output")
            st.code(lint_out or lint_err, language="bash")

        review_sections = []

        # 3️⃣ Style Checker
        if review_mode == "Style Checker":
            if uploaded_convention:
                convention_rules = load_convention_file(uploaded_convention)
                violations = check_code_style_against_rules(code_content, convention_rules)
                if not violations:
                    st.success("✅ Code tuân thủ toàn bộ convention!")
                else:
                    for v in violations:
                        formatted = (
                            f"### 🧹 **Rule:** `{v['Rule']}`\n"
                            f"**Severity:** 🟡 `{v['Severity']}`  \n"
                            f"**Description:** {v['Description']}\n\n"
                            f"```python\n{v['Example']}\n```\n\n"
                            f"💡 **Suggestion:**\n> {v['Suggestion']}\n"
                            f"---"
                        )
                        review_sections.append(formatted)
            else:
                st.warning("⚠️ Vui lòng upload file Coding Convention Excel để kiểm tra style.")

        # 4️⃣ Performance Expert
        elif review_mode == "Performance Expert":
            st.markdown("### 🧠 Phân tích hiệu năng & logic")
            chunks = chunk_text(code_content)
            for idx, chunk in enumerate(chunks, 1):
                prompt = (
                    f"Bạn là chuyên gia hiệu năng & logic code.\n"
                    f"Phân tích đoạn code sau và chỉ ra:\n"
                    f"- Lỗi logic, hiệu năng, bug tiềm ẩn\n"
                    f"- Đưa ra gợi ý sửa cụ thể\n\n"
                    f"Code:\n```{detected_lang}\n{chunk}\n```\n"
                    f"Hãy trả về nội dung Markdown gọn gàng, highlight từng issue."
                )
                analysis = summarize_with_llm([
                    {"role": "system", "content": "Bạn là Performance Expert phân tích code chi tiết."},
                    {"role": "user", "content": prompt}
                ])
                review_sections.append(f"### 🔍 Phần {idx}\n{analysis}\n---")

        # 5️⃣ Lưu kết quả
        st.session_state.review_results = [{
            "file": uploaded_file.name,
            "review": review_sections
        }]
        st.success("✅ Review hoàn tất! Xem kết quả ở tab Review.")
        st.rerun()
