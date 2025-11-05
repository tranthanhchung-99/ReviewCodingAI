# ================================================
# File: LANGUAGES.py
# Mô tả: Đa ngôn ngữ cho giao diện Streamlit (Việt / Anh)
# Dự án: Bug Busters 🧩
# ================================================

LANGUAGES = {
    "vi": {
        "upload": "Tải lên file cần review",
        "upload_req": "Tải lên file requirement",
        "start_review": "Bắt đầu Review",
        "clear_chat": "Xóa Chat",
        "generate_test": "Sinh Test Case",
        "chat_tab": "💬 Chat",
        "testcase_tab": "🧪 Test Cases",
        "testcase_history": "### 🧪 Lịch sử Test Case được sinh ra",
        "no_testcase": (
            "Chưa có test case nào. Hãy tạo bằng nút **Sinh Test Case** trong sidebar."
        ),
        "testcase": "Test Case",
        "download_testcase": "💾 Tải test case (.json)",
        "processing_file": "🔍 Đang xử lý file...",
        "ocr_success": "✅ Đã nhận diện text từ ảnh!",
        "file_large": "File quá lớn ({size} ký tự), chỉ review phần đầu!",
        "no_issue": "✅ Không phát hiện lỗi!",
        "review_done": (
            "✅ Review đã hoàn tất! Bạn có thể hỏi thêm chi tiết "
            "hoặc yêu cầu gợi ý fix lỗi nhé."
        ),
        "file": "File",
        "chunk": "Phần",
        "error": "Lỗi",
        "original_code": "**Code gốc:**",
        "suggested_code": "**Code đề xuất:**",
        "ask_ai": "💬 Hỏi AI về code hoặc yêu cầu review thêm...",
        "testcase_warning": "⚠️ Hãy review code trước khi tạo test case nhé!",
        "generating_testcase": "🧪 Đang tạo test case...",
        "testcase_success": "✅ Đã tạo test case thành công!",
        "testcase_added": (
            "🧪 Đã tạo test case! Bạn có thể xem trong tab **Test Cases** hoặc tải về."
        ),
    },
    "en": {
        "upload": "Upload file to review",
        "upload_req": "Upload file requirement",
        "start_review": "Start Review",
        "clear_chat": "Clear Chat",
        "generate_test": "Generate Test Case",
        "chat_tab": "💬 Chat",
        "testcase_tab": "🧪 Test Cases",
        "testcase_history": "### 🧪 Generated Test Case History",
        "no_testcase": "No test cases yet. Use **Generate Test Case** in sidebar.",
        "testcase": "Test Case",
        "download_testcase": "💾 Download test cases (.json)",
        "processing_file": "🔍 Processing file...",
        "ocr_success": "✅ Text extracted from image!",
        "file_large": "File is too large ({size} chars), only first part is reviewed!",
        "no_issue": "✅ No issues found!",
        "review_done": (
            "✅ Review complete! You can ask for more details or request fix suggestions."
        ),
        "file": "File",
        "chunk": "Chunk",
        "error": "Error",
        "original_code": "**Original code:**",
        "suggested_code": "**Suggested code:**",
        "ask_ai": "💬 Ask AI about code or request more reviews...",
        "testcase_warning": "⚠️ Please review code before generating test cases!",
        "generating_testcase": "🧪 Generating test cases...",
        "testcase_success": "✅ Test cases generated successfully!",
        "testcase_added": (
            "🧪 Test case created! See it in **Test Cases** tab or download."
        ),
    },
}


def get_text(lang: str, key: str) -> str:
    """
    Hàm tiện ích để lấy text theo ngôn ngữ hiện tại.
    Nếu không tìm thấy key, trả về chính key đó.
    """
    return LANGUAGES.get(lang, LANGUAGES["en"]).get(key, key)
