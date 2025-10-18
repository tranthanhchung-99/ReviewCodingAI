import os
import tempfile
import zipfile
import subprocess
from pathlib import Path
import streamlit as st
from openai import AzureOpenAI
from dotenv import load_dotenv
from PIL import Image
import pytesseract
import json

# =========================
# CONFIG
# =========================
load_dotenv()
client = AzureOpenAI(
    api_version="2024-07-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)
MODEL = "gpt-4o-mini"

st.set_page_config(page_title="💬 AI Code Reviewer", layout="wide")

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
# STYLE
# =========================
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #e6f2ff, #f7faff);
}
.main {
    padding: 0 !important;
}
header, footer {visibility: hidden;}
/* Header */
.topbar {
    display: flex;
    align-items: center;
    justify-content: center;
    background: white;
    box-shadow: 0 3px 15px rgba(0,0,0,0.05);
    padding: 18px 0;
    border-radius: 0 0 25px 25px;
    margin-bottom: 20px;
}
.topbar img {
    width: 45px;
    margin-right: 10px;
}
.topbar h1 {
    font-size: 26px;
    color: #0b2545;
    font-weight: 700;
}

/* Chat container */
.chat-box {
    background: rgba(255,255,255,0.9);
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    height: 65vh;
    overflow-y: auto;
    margin: auto;
    width: 80%;
}

/* Chat input */
.stChatInputContainer {
    width: 80% !important;
    margin: 10px auto 40px auto !important;
}
.stChatInput {
    border-radius: 25px !important;
    box-shadow: 0 3px 8px rgba(0,0,0,0.1) !important;
}
.stChatInput:focus-within {
    outline: none !important;
    border: none !important;
    box-shadow: 0 3px 10px rgba(80,150,255,0.3) !important;
}

/* Buttons */
.sidebar-buttons button {
    border-radius: 30px;
    width: 100%;
    font-weight: 600;
    margin-bottom: 10px;
    transition: 0.2s;
}
.sidebar-buttons button:hover {
    transform: scale(1.03);
}

/* Scrollbar */
.chat-box::-webkit-scrollbar {
    width: 8px;
}
.chat-box::-webkit-scrollbar-thumb {
    background-color: #a3c7ff;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown("""
<div class="topbar">
    <img src="https://cdn-icons-png.flaticon.com/512/4712/4712038.png">
    <h1>AI Code Reviewer</h1>
</div>
""", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
st.sidebar.markdown("## ⚙️ Settings")
with st.sidebar:
    upload = st.file_uploader("📂 Upload file / ZIP / Image", type=["zip", "py", "js", "java", "ts", "png", "jpg"])
    reviewer_type = st.selectbox("Reviewer Mode", [
        "Mentor (Giải thích dễ hiểu)",
        "Senior Dev (Phân tích chuyên sâu)",
        "Security Expert (Bảo mật)",
        "Style Checker (Code format)"
    ])
    run_btn = st.button("🚀 Start Review", use_container_width=True)
    clear_btn = st.button("🧹 Clear Chat", use_container_width=True)
    generate_tests_btn = st.button("🧪 Generate Test Cases", use_container_width=True)

# =========================
# TAB VIEW
# =========================   
tab1, tab2 = st.tabs(["💬 Chat", "🧪 Test Cases"])

with tab1:
    # phần hiển thị chat (đoạn bạn đã có)
    for msg in st.session_state.chat_history:
        avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

with tab2:
    st.markdown("### 🧪 Lịch sử Test Case được sinh ra")
    if not st.session_state.test_cases:
        st.info("Chưa có test case nào. Hãy tạo bằng nút **Generate Test Cases** trong sidebar.")
    else:
        for i, tc in enumerate(st.session_state.test_cases, 1):
            with st.expander(f"Test Case #{i}: {tc.get('description', '')[:60]}"):
                st.json(tc)

        # Nút tải về
        test_json = json.dumps(st.session_state.test_cases, ensure_ascii=False, indent=2)
        st.download_button(
            label="💾 Tải test case (.json)",
            data=test_json,
            file_name="test_cases.json",
            mime="application/json"
        )

# =========================
# HELPER FUNCS
# =========================

def run_command(cmd, cwd=None, timeout=20):
    """Chạy lệnh shell (ví dụ: flake8) và trả về kết quả"""
    try:
        r = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def safe_read_text(path: Path):
    """Đọc file text an toàn, bỏ qua lỗi encoding"""
    return path.read_text(encoding="utf-8", errors="ignore")

def summarize_with_llm(messages):
    """Gửi yêu cầu tới Azure OpenAI để tóm tắt / review code"""
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=800,
        temperature=0.0,
    )
    return resp.choices[0].message.content.strip()

def extract_text_from_image(img_file):
    """OCR: Trích xuất text từ ảnh bằng pytesseract"""
    img = Image.open(img_file)
    return pytesseract.image_to_string(img, lang="eng")

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
    with st.spinner("🔍 Đang xử lý file..."):
        tmp = Path(tempfile.mkdtemp(prefix="ai-review-"))
        files_to_review = []
        extracted_texts = []

        # Nếu là ảnh: dùng OCR để đọc nội dung text
        if upload.type.startswith("image/"):
            text = extract_text_from_image(upload)
            extracted_texts.append({"filename": upload.name, "content": text})
            st.success("✅ Đã nhận diện text từ ảnh!")

        else:
            # Lưu file tạm
            save_path = tmp / upload.name
            with open(save_path, "wb") as f:
                f.write(upload.getbuffer())

            # Nếu là ZIP: giải nén tất cả file code bên trong
            if upload.name.endswith(".zip"):
                with zipfile.ZipFile(save_path, "r") as z:
                    z.extractall(tmp)
                for p in tmp.rglob("*"):
                    if p.suffix in {".py", ".js", ".ts", ".java"}:
                        files_to_review.append(p)
            else:
                files_to_review.append(save_path)

        results = []
        for f in files_to_review or extracted_texts:
            if isinstance(f, dict):  # trường hợp ảnh
                fname = f["filename"]
                content = f["content"]
                linter_out = "(Không áp dụng cho ảnh)"
            else:
                fname = f.name
                content = safe_read_text(f)
                linter_out = ""

                # Nếu là Python => chạy linter flake8
                if f.suffix == ".py":
                    _, out, err = run_command(f"flake8 {f}", cwd=tmp)
                    linter_out = (out + "\n" + err).strip() or "(No issues found)"

            # Gửi nội dung cho AI để review
            prompt = f"""
You are an expert code reviewer.
File name: {fname}
Linter output: {linter_out}

Code content (first 3000 chars):
{content[:3000]}

Please return JSON with keys: summary, issues[].
"""
            response = summarize_with_llm([
                {"role": "system", "content": "You are a senior software engineer reviewing code for quality and security."},
                {"role": "user", "content": prompt}
            ])

            # Parse kết quả JSON
            try:
                parsed = json.loads(response)
            except:
                parsed = {"summary": response}

            results.append({"file": fname, "review": parsed})

        # Lưu kết quả review vào session
        st.session_state.review_results = results

        # Hiển thị thông báo trong khung chat
        # with st.chat_message("assistant", avatar="🤖"):
        #     st.markdown("✅ **Review hoàn tất!** Bạn có thể hỏi tôi chi tiết về lỗi hoặc cách sửa code.")
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "✅ Review đã hoàn tất! Bạn có thể hỏi thêm chi tiết hoặc yêu cầu gợi ý fix lỗi nhé."
        })

# =========================
# CHAT HIỂN THỊ
# =========================
for msg in st.session_state.chat_history:
    avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# =========================
# CHAT INPUT
# =========================
user_input = st.chat_input("💬 Hỏi AI về code hoặc yêu cầu review thêm...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_input)

    # Lấy ngữ cảnh từ các kết quả review gần đây
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
# GENERATE TEST CASES
# =========================
if generate_tests_btn:
    if not st.session_state.review_results:
        st.warning("⚠️ Hãy review code trước khi tạo test case nhé!")
    else:
        with st.spinner("🧪 Đang tạo test case..."):
            code_context = ""
            for r in st.session_state.review_results:
                if "file" in r and "review" in r:
                    code_context += f"File: {r['file']}\n{r['review'].get('summary', '')[:1000]}\n"

            prompt = f"""
Generate detailed and practical test cases for the reviewed code below.
Include both **normal** and **edge cases**, and format the result as a JSON list:
[
  {{
    "description": "Mô tả test case",
    "input": "...",
    "expected_output": "..."
  }}
]
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
            st.success("✅ Đã tạo test case thành công!")

            # Ghi vào chat
            # with st.chat_message("assistant", avatar="🤖"):
            #     st.markdown("🧪 **Đã tạo test case mới!** Xem trong tab Test Cases.")
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "🧪 Đã tạo test case! Bạn có thể xem trong tab **Test Cases** hoặc tải về."
            })
            st.rerun()
# =========================
# AUTO-SCROLL JS
# =========================
st.markdown("""
<script>
    var chatBox = window.parent.document.querySelector('.chat-box');
    if (chatBox) {
        chatBox.scrollTop = chatBox.scrollHeight;
    }
</script>
""", unsafe_allow_html=True)
