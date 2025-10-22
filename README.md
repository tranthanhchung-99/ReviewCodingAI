# AI Code Reviewer

Ứng dụng review code tự động bằng Azure OpenAI, hỗ trợ kiểm tra coding convention, phân tích bảo mật, sinh test case và đa ngôn ngữ (Việt/Anh).  
Giao diện thao tác dễ dùng, cho phép tải lên code, ZIP hoặc ảnh OCR để review, hỏi đáp trực tiếp với AI.

---

## 1. Cấu trúc thư mục
ai-code-reviewer/ 
├── main.py # File chạy chính, giao diện Streamlit 
├── utils.py # Hàm tiện ích xử lý code, OCR, gọi OpenAI 
├── LANGUAGES.py # Module đa ngôn ngữ cho giao diện 
├── .env # Thông tin API key và endpoint Azure OpenAI 
├── README.md # Hướng dẫn sử dụng chi tiết

---

## 2. Hướng dẫn cài môi trường

	### Bước 1: Cài đặt Python

	- Yêu cầu Python >= 3.9
	- Kiểm tra bằng lệnh:

	### Bước 2: Clone mã nguồn
	git clone https://github.com/yourname/ai-code-reviewer.git cd ai-code-reviewer

	### Bước 3: Cài đặt các thư viện cần thiết
	pip install streamlit openai python-dotenv pillow pytesseract
	> Nếu chạy trên Windows, cần cài thêm Tesseract OCR: [Download tại đây](https://github.com/tesseract-ocr/tesseract)  
	> Nếu chạy trên Linux/macOS, dùng lệnh:  
	> ```
	> sudo apt-get install tesseract-ocr
	> ```

	### Bước 4: Tạo file `.env`
	Thay bằng endpoint và API Key thực tế từ Azure OpenAI Portal.

---

## 3. Chạy ứng dụng

```bash
streamlit run main.py

4. Hướng dẫn thao tác trên giao diện

Sidebar
Chọn ngôn ngữ: Tiếng Việt hoặc English.
Upload file: Chọn file code (.py, .js, .java, .ts), ZIP hoặc ảnh (PNG, JPG).
Reviewer Mode: Chọn kiểu review:
Mentor: Giải thích dễ hiểu
Senior Dev: Phân tích chuyên sâu
Security Expert: Phân tích bảo mật
Style Checker: Kiểm tra format code

Các nút chức năng:
Bắt đầu Review: Gửi code lên AI để phân tích, nhận kết quả review.
Xóa Chat: Xóa toàn bộ lịch sử chat, review hiện tại.
Sinh Test Case: Sau khi review, nhấn để AI sinh bộ test case cho code.

Tab Chat
Hiển thị lịch sử chat giữa bạn và AI.
Có thể nhập câu hỏi vào khung chat để hỏi về lỗi, giải thích code, yêu cầu gợi ý fix, hoặc bất kỳ vấn đề nào liên quan đến code vừa review.

Tab Test Cases
Hiển thị các test case đã sinh ra cho code của bạn.
Có thể tải về file .json các test case để sử dụng cho dự án thực tế.

Kết quả Review
Khi review hoàn tất, sẽ hiển thị:
Tóm tắt kết quả review từng file.
Danh sách lỗi/phân tích, có thể mở rộng xem chi tiết.
Nếu AI gợi ý code đã refactor/sửa, sẽ hiển thị song song code gốc và code đề xuất.