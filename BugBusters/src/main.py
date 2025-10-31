import sys, os
from pathlib import Path

# =========================================
# 🔧 FIX: thêm thư mục gốc dự án vào PYTHONPATH
# =========================================
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
print("✅ Added to sys.path:", BASE_DIR)

# =========================================
# IMPORTS
# =========================================
import tempfile
import zipfile
import json
import streamlit as st
from openai import AzureOpenAI
from dotenv import load_dotenv

# ✅ Import từ utils (đã hỗ trợ OCR + Vision)
from utils.chunk_utils import chunk_text
from utils.utils import (
    safe_read_text,
    run_command,
    summarize_with_llm,
    extract_text_from_image,
    analyze_image_with_llm
)
from utils.LANGUAGES import LANGUAGES

# =========================
# CONFIG
# =========================
load_dotenv()

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01"
)

MODEL = "gpt-4o-mini"
MAX_FILE_SIZE = 100_000  # ký tự

st.set_page_config(page_title="💬 Bug Busters", layout="wide")

# =========================
# LANGUAGE
# =========================
lang = st.sidebar.selectbox("Ngôn ngữ / Language", ["vi", "en"])
T = LANGUAGES[lang]

# =========================
# SESSION STATE
# =========================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "review_results" not in st.session_state:
    st.session_state.review_results = []
if "test_cases" not in st.session_state:
    st.session_state.test_cases = []

# =========================
# SIDEBAR
# =========================
st.sidebar.markdown("## ⚙️ Settings")
upload = st.sidebar.file_uploader(
    T["upload"],
    type=["zip", "py", "js", "java", "ts", "png", "jpg", "jpeg"]
)
reviewer_type = st.sidebar.selectbox("Reviewer Mode", [
    "Mentor (Giải thích dễ hiểu)",
    "Senior Dev (Phân tích chuyên sâu)",
    "Security Expert (Bảo mật)",
    "Style Checker (Code format)"
])
run_btn = st.sidebar.button(T["start_review"], use_container_width=True)
clear_btn = st.sidebar.button(T["clear_chat"], use_container_width=True)
generate_tests_btn = st.sidebar.button(T["generate_test"], use_container_width=True)

# =========================
# TAB STYLE (HEADER FIX)
# =========================
st.markdown("""
    <style>
    div[role="tablist"] {
        position: fixed !important;
        top:50px;
        background-color: white;
        z-index: 9999;
        padding-top: 10px;
        width: 100%
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# TAB SETUP
# =========================
tab1, tab2 = st.tabs([T["chat_tab"], T["testcase_tab"]])

# =========================
# TAB 1 — REVIEW / CHAT
# =========================
with tab1:
    for msg in st.session_state.chat_history:
        avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    if st.session_state.review_results:
        for r in st.session_state.review_results:
            st.markdown(f"### 📄 {T['file']}: {r['file']}")
            for idx, review in enumerate(r["review"], 1):
                st.markdown(f"**{T['chunk']} {idx}:** {review.get('summary', '')}")
                if review.get('issues'):
                    for i, iss in enumerate(review['issues'], 1):
                        with st.expander(f"{T['error']} #{i}"):
                            st.write(iss)
                else:
                    st.success(T["no_issue"])
                if review.get('suggested_code'):
                    st.code(review['suggested_code'], language="python")

# =========================
# TAB 2 — TEST CASE
# =========================
with tab2:
    st.markdown(T["testcase_history"])
    if not st.session_state.test_cases:
        st.info(T["no_testcase"])
    else:
        for i, tc in enumerate(st.session_state.test_cases, 1):
            with st.expander(f"{T['testcase']} #{i}: {tc.get('description', '')[:60]}"):
                st.json(tc)
        test_json = json.dumps(st.session_state.test_cases, ensure_ascii=False, indent=2)
        st.download_button(
            label=T["download_testcase"],
            data=test_json,
            file_name="test_cases.json",
            mime="application/json"
        )

# =========================
# CLEAR CHAT
# =========================
if clear_btn:
    st.session_state.chat_history.clear()
    st.session_state.review_results.clear()
    st.rerun()

# =========================
# XỬ LÝ FILE UPLOAD & REVIEW
# =========================
if run_btn and upload:
    with st.spinner(T["processing_file"]):
        tmp = Path(tempfile.mkdtemp(prefix="bugbusters-"))
        files_to_review = []
        extracted_texts = []

        # 🖼️ Nếu là ảnh → OCR + Vision + phục hồi code
        if upload.type.startswith("image/"):
            st.info("🖼️ Ảnh được phát hiện — đang trích xuất nội dung...")

            raw_text = extract_text_from_image(upload)
            if not raw_text.strip():
                st.error("⚠️ Không tìm thấy nội dung nào trong ảnh.")
            else:
                st.info("📄 Text OCR được trích xuất:")
                st.code(raw_text[:800], language="markdown")

            # Lưu ảnh tạm để AI vision đọc
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                tmp_img.write(upload.getvalue())
                tmp_img_path = tmp_img.name

            # Vision model phân tích ảnh
            ai_analysis = analyze_image_with_llm(tmp_img_path)
            st.info("🤖 Phân tích AI (Vision model):")
            st.markdown(ai_analysis)

            # Dùng LLM để làm sạch và khôi phục code từ OCR
            st.info("🧩 Đang phục hồi code từ ảnh...")
            clean_prompt = f"""
Dưới đây là phần text được trích xuất bằng OCR từ ảnh:

Hãy:
1. Nhận diện phần code có trong nội dung (nếu có).
2. Sửa các lỗi OCR như ký tự sai, thiếu dấu ngoặc, indent hỏng.
3. Giữ nguyên định dạng và comment.
4. Trả về **chỉ đoạn code sạch**, không thêm mô tả hay lời giải thích.
"""
            cleaned_code = summarize_with_llm([
                {"role": "system", "content": "Bạn là chuyên gia phục hồi code từ ảnh chụp."},
                {"role": "user", "content": clean_prompt + "\n\n" + raw_text}
            ])

            # 🔍 Đoán ngôn ngữ code và gán phần mở rộng hợp lệ
            detected_lang = "python"
            ext_map = {
                "python": ".py",
                "java": ".java",
                "cpp": ".cpp",
                "javascript": ".js",
                "html": ".html"
            }
            lc = cleaned_code.lower()
            if "public class" in lc or "system.out.println" in lc:
                detected_lang = "java"
            elif "#include" in lc or "printf(" in lc:
                detected_lang = "cpp"
            elif "function" in lc or "const" in lc:
                detected_lang = "javascript"
            elif "<html" in lc:
                detected_lang = "html"

            file_ext = ext_map.get(detected_lang, ".py")

            # 💡 In ra code nhận diện được
            st.success(f"✅ Code được nhận diện ({detected_lang}):")
            st.code(cleaned_code, language=detected_lang)

            # Thêm vào danh sách review
            extracted_texts.append({
                "filename": f"{upload.name}_ocr{file_ext}",
                "content": cleaned_code
            })
            st.success("🎯 Code trong ảnh đã sẵn sàng để review!")

        else:
            # =========================
            # FILE CODE HOẶC ZIP
            # =========================
            save_path = tmp / upload.name
            with open(save_path, "wb") as f:
                f.write(upload.getbuffer())

            if upload.name.endswith(".zip"):
                with zipfile.ZipFile(save_path, "r") as z:
                    z.extractall(tmp)
                for p in tmp.rglob("*"):
                    if p.suffix in {".py", ".js", ".ts", ".java", ".cpp", ".c", ".html", ".css"}:
                        files_to_review.append(p)
            else:
                files_to_review.append(save_path)

        # =========================
        # DUYỆT CÁC FILE VÀ REVIEW
        # =========================
        results = []
        for f in files_to_review or extracted_texts:
            if isinstance(f, dict):  # OCR từ ảnh
                fname = f["filename"]
                content = f["content"]
                linter_out = "(Không áp dụng cho ảnh)"
            else:
                fname = f.name
                content = safe_read_text(f)
                linter_out = ""
                if len(content) > MAX_FILE_SIZE:
                    st.warning(T["file_large"].format(size=len(content)))
                    content = content[:MAX_FILE_SIZE]
                st.code(content[:1000], language=f.suffix.replace('.', ''))

                if f.suffix == ".py":
                    _, out, err = run_command(f"flake8 {f}", cwd=tmp)
                    linter_out = (out + "\n" + err).strip() or T["no_issue"]

            file_ext = os.path.splitext(fname)[1].lower()
            if file_ext in [".png", ".jpg", ".jpeg"]:
                chunks = [content]
            else:
                chunks = chunk_text(content, ext=file_ext)

            review_chunk_results = []
            for idx, chunk in enumerate(chunks):
                prompt = f"""
Bạn là reviewer code. Hãy phân tích phần {idx+1}/{len(chunks)} trong file {fname}.
Linter output: {linter_out}
Code hoặc nội dung:
{chunk}
Hãy trả về JSON gồm: summary, issues[], suggested_code (nếu có).
"""
                system_prompt = {
                    "Mentor (Giải thích dễ hiểu)": "Bạn là mentor, hãy giải thích code dễ hiểu cho người mới.",
                    "Senior Dev (Phân tích chuyên sâu)": "Bạn là senior developer, hãy phân tích code chi tiết.",
                    "Security Expert (Bảo mật)": "Bạn là chuyên gia bảo mật, hãy tập trung vào các điểm yếu.",
                    "Style Checker (Code format)": "Bạn là chuyên gia kiểm tra format code."
                }[reviewer_type]

                response = summarize_with_llm([
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ])

                try:
                    parsed = json.loads(response)
                except:
                    parsed = {"summary": response}
                review_chunk_results.append(parsed)

            results.append({"file": fname, "review": review_chunk_results})

        st.session_state.review_results = results
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": T["review_done"]
        })
        st.rerun()
