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

# ✅ Import từ thư mục utils
from utils.chunk_utils import chunk_text
from utils.utils import safe_read_text, run_command, summarize_with_llm, extract_text_from_image
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
upload = st.sidebar.file_uploader(T["upload"], type=["zip", "py", "js", "java", "ts", "png", "jpg"])
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
# TAB VIEW
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

tab1, tab2 = st.tabs([T["chat_tab"], T["testcase_tab"]])

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
        file_ext = upload.name.split('.')[-1]

        # 🖼️ Nếu là ảnh: dùng OCR
        if upload.type.startswith("image/"):
            text = extract_text_from_image(upload)
            extracted_texts.append({"filename": upload.name, "content": text})
            st.success(T["ocr_success"])
        else:
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

        results = []
        for f in files_to_review or extracted_texts:
            if isinstance(f, dict):  # ảnh OCR
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
                st.code(content[:1000], language=file_ext)

                if f.suffix == ".py":
                    _, out, err = run_command(f"flake8 {f}", cwd=tmp)
                    linter_out = (out + "\n" + err).strip() or T["no_issue"]

            # ✅ Gọi chunk_text mới (Tree-sitter nếu build được, fallback nếu không)
            chunks = chunk_text(content, ext=os.path.splitext(fname)[1])

            review_chunk_results = []
            for idx, chunk in enumerate(chunks):
                prompt = f"""
Bạn là reviewer code. Hãy phân tích phần {idx+1}/{len(chunks)} trong file {fname}.
Linter output: {linter_out}
Code:
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

# =========================
# CHAT
# =========================
user_input = st.chat_input(T["ask_ai"])
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_input)

    context_text = ""
    if st.session_state.review_results:
        for r in st.session_state.review_results[:3]:
            ctx = json.dumps(r, ensure_ascii=False)[:1500]
            context_text += f"\n{ctx}\n"

    messages = [
        {"role": "system", "content": "You are a friendly AI code reviewer."},
        {"role": "user", "content": f"Previous review context:\n{context_text}\nUser query:\n{user_input}"}
    ]
    answer = summarize_with_llm(messages)
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(answer)

# =========================
# TEST CASE GENERATION
# =========================
if generate_tests_btn:
    if not st.session_state.review_results:
        st.warning(T["testcase_warning"])
    else:
        with st.spinner(T["generating_testcase"]):
            code_context = ""
            for r in st.session_state.review_results:
                if "file" in r and "review" in r:
                    code_context += f"File: {r['file']}\n{r['review'][0].get('summary', '')[:1000]}\n"

            prompt = f"""
Generate detailed and practical test cases for the reviewed code below.
Include both **normal** and **edge cases**, and format the result as a JSON list.
Code context:
{code_context}
"""

            result = summarize_with_llm([
                {"role": "system", "content": "You are an expert QA engineer specializing in software test case design."},
                {"role": "user", "content": prompt}
            ])
            try:
                parsed = json.loads(result)
            except:
                parsed = [{"description": "Raw output", "input": "", "expected_output": result}]
            st.session_state.test_cases.extend(parsed)
            st.success(T["testcase_success"])
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": T["testcase_added"]
            })
            st.rerun()
