import pandas as pd

def load_convention_file(convention_file):
    """
    Đọc và chuẩn hóa file Coding Convention (Excel).
    Trả về:
        - rules: list[dict]
        - convention_text: str
    """
    try:
        df = pd.read_excel(convention_file)
        df = df.fillna("")

        # Kiểm tra cột bắt buộc
        required_cols = ["Rule", "Description"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Thiếu cột bắt buộc '{col}' trong file convention.")

        # Chuẩn hóa dữ liệu
        rules = df.to_dict(orient="records")

        # Text tóm tắt convention — dùng để gửi vào LLM
        convention_text = "\n".join([
            f"- {r.get('Rule', '').strip()}: {r.get('Description', '').strip()}"
            for r in rules if r.get("Rule")
        ])

        return rules, convention_text

    except Exception as e:
        raise RuntimeError(f"❌ Lỗi khi đọc file convention: {e}")
