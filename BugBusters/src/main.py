import sys, os, tempfile, zipfile, json
from pathlib import Path
import streamlit as st
import pandas as pd
from openai import AzureOpenAI
from dotenv import load_dotenv

# =========================
# 🔧 PATH FIX
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
print("✅ Added to sys.path:", BASE_DIR)

# =========================
# IMPORTS
# =========================
from utils.utils import (
    safe_read_text,
    run_command,
    summarize_with_llm,
    extract_text_from_image,
    analyze_image_with_llm,
    chunk_text
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
MAX_FILE_SIZE = 100_000

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
if "coding_rules" not in st.session_state:
    st.session_state.coding_rules = []

# =========================
# SIDEBAR
# =========================
st.sidebar.markdown("## ⚙️ Settings")

upload = st.sidebar.file_uploader(
    T["upload"], type=["zip", "py", "js", "java", "ts", "cpp", "c", "html", "css", "png", "jpg"]
)
convention_file = st.sidebar.file_uploader(
    T["upload_req"], type=["xlsx", "xls"]
)
reviewer_type = st.sidebar.selectbox("Reviewer Mode", [
    "Style Checker",
    "Performance Expert",
    "Free Review"
])

run_btn = st.sidebar.button(T["start_review"], use_container_width=True)
clear_btn = st.sidebar.button(T["clear_chat"], use_container_width=True)

# =========================
# LOAD CONVENTION FILE
# =========================
if convention_file:
    try:
        df = pd.read_excel(convention_file)
        st.session_state.coding_rules = df.to_dict(orient="records")
        st.sidebar.success(f"📘 Đã tải {len(df)} quy tắc từ file convention.")
    except Exception as e:
        st.sidebar.error(f"❌ Lỗi đọc file convention: {e}")

# =========================
# STYLE
# =========================
st.markdown("""
    <style>
        header[data-testid="stHeader"] div[role="banner"] div:nth-child(1) {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        #MainMenu {visibility: hidden !important;}
    </style>
""", unsafe_allow_html=True)

# =========================
# MAIN AREA
# =========================
for msg in st.session_state.chat_history:
    avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

if clear_btn:
    st.session_state.chat_history.clear()
    st.session_state.review_results.clear()
    st.rerun()

# =========================
# REVIEW HANDLER
# =========================
if run_btn and upload:
    with st.spinner(T["processing_file"]):
        tmp = Path(tempfile.mkdtemp(prefix="bugbusters-"))
        files_to_review = []
        extracted_texts = []

        # 🖼️ IMAGE HANDLING
        if upload.type.startswith("image/"):
            st.info("🖼️ Đang trích xuất code từ ảnh...")
            raw_text = extract_text_from_image(upload)
            st.code(raw_text[:500], language="markdown")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                tmp_img.write(upload.getvalue())
                tmp_img_path = tmp_img.name

            ai_analysis = analyze_image_with_llm(tmp_img_path)
            st.markdown(ai_analysis)
            extracted_texts.append({"filename": f"{upload.name}_ocr.py", "content": raw_text})

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
        convention_text = "\n".join([
            f"- {r.get('Rule', '')}: {r.get('Description', '')}"
            for r in st.session_state.coding_rules if r.get('Rule')
        ]) if st.session_state.coding_rules else ""

        for f in files_to_review or extracted_texts:
            if isinstance(f, dict):
                fname = f["filename"]
                content = f["content"]
                linter_out = "(Không áp dụng cho ảnh)"
            else:
                fname = f.name
                content = safe_read_text(f)
                _, out, err = run_command(f"flake8 {f}", cwd=tmp)
                linter_out = (out + "\n" + err).strip() or T["no_issue"]

            chunks = chunk_text(content, ext=os.path.splitext(fname)[1])
            review_chunk_results = []
            violated_rules = []

            for idx, chunk in enumerate(chunks):
                if reviewer_type == "Style Checker":
                    prompt = f"""
Bạn là chuyên gia kiểm tra coding convention.
Dựa theo file quy tắc sau:
{convention_text if convention_text else "(Không có quy tắc cụ thể)"}

Code cần review (phần {idx+1} của {fname}):
{chunk}

Hãy trả về JSON:
{{
 "summary": "...",
 "issues": ["..."],
 "suggested_code": "..."
}}
"""
                elif reviewer_type == "Performance Expert":
                    prompt = f"""
Bạn là chuyên gia phân tích code nâng cao (logic, hiệu năng, bảo mật).
Không cần xét convention.

Code cần review (phần {idx+1} của {fname}):
{chunk}

Hãy trả về JSON:
{{
 "summary": "...",
 "issues": ["..."],
 "suggested_code": "..."
}}
"""
                else:
                    prompt = f"""
Bạn là trợ lý AI. Hãy đọc đoạn code sau và nhận xét tự nhiên, không cần JSON.
{chunk}
"""

                response = summarize_with_llm([
                    {"role": "system", "content": "Bạn là chuyên gia review code."},
                    {"role": "user", "content": prompt}
                ])

                try:
                    parsed = json.loads(response)
                except:
                    parsed = {"summary": response, "issues": [], "suggested_code": ""}

                # Kiểm tra rule nào bị vi phạm
                if reviewer_type == "Style Checker" and st.session_state.coding_rules:
                    for rule in st.session_state.coding_rules:
                        keyword = str(rule.get("Keyword", "")).strip()
                        if keyword and keyword in chunk:
                            violated_rules.append(rule)

                review_chunk_results.append(parsed)

            results.append({"file": fname, "violated_rules": violated_rules, "review": review_chunk_results})

        st.session_state.review_results = results
        st.session_state.chat_history.append({"role": "assistant", "content": T["review_done"]})
        st.rerun()

# =========================
# HIỂN THỊ KẾT QUẢ REVIEW
# =========================
if st.session_state.review_results:
    for r in st.session_state.review_results:
        st.markdown(f"### 📄 File: {r['file']}")
        if r.get("violated_rules"):
            st.warning("⚠️ Các quy tắc convention bị vi phạm:")
            st.dataframe(pd.DataFrame(r["violated_rules"]))
        for idx, rev in enumerate(r["review"], 1):
            st.markdown(f"**Phần {idx}:** {rev.get('summary', '')}")
            if rev.get("issues"):
                for i, issue in enumerate(rev["issues"], 1):
                    st.markdown(f"- ❌ {issue}")
            if rev.get("suggested_code"):
                st.code(rev["suggested_code"], language="python")

# =========================
# CHAT
# =========================
user_input = st.chat_input(T["ask_ai"])
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    context = "\n".join([r["file"] for r in st.session_state.review_results]) if st.session_state.review_results else ""
    messages = [
        {"role": "system", "content": "Bạn là AI hỗ trợ review code."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{user_input}"}
    ]
    ans = summarize_with_llm(messages)
    st.session_state.chat_history.append({"role": "assistant", "content": ans})
    st.rerun()
