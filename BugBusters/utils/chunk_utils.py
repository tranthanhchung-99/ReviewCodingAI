"""
utils/chunk_utils.py
---------------------
Chức năng:
- Tách (chunk) code theo cấu trúc logic (function, class, method)
- Hỗ trợ tự động đa ngôn ngữ (40+)
- Fallback chia theo ký tự nếu không phân tích được
"""

import re
import os
from typing import List
from tree_sitter import Language, Parser


# =======================================
# 1️⃣ Cấu hình chung
# =======================================

LANGUAGE_SO_PATH = os.path.join("build", "my-languages.so")

# Nếu bạn đã build từ build_languages.py thì file này đã có.
# Tree-sitter cho phép load nhiều ngôn ngữ cùng 1 file .so

# Các phần mở rộng file tương ứng với tên ngôn ngữ
SUPPORTED_LANGS = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".cs": "c_sharp",
    ".go": "go",
    ".rs": "rust",
    ".php": "php",
    ".rb": "ruby",
    ".lua": "lua",
    ".json": "json",
    ".html": "html",
    ".css": "css",
    ".sql": "sql",
    ".md": "markdown",
    ".sh": "bash",
    ".pl": "perl",
    ".kt": "kotlin",
    ".swift": "swift",
    ".scala": "scala",
    ".dart": "dart",
    ".r": "r",
    ".hs": "haskell",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".toml": "toml",
    ".xml": "xml",
    ".vue": "vue",
    ".svelte": "svelte",
    ".dockerfile": "dockerfile",
    ".graphql": "graphql",
    ".ini": "ini",
    ".ex": "elixir",
    ".erl": "erlang",
    ".nim": "nim",
    ".zig": "zig",
}


# Cache parser để tránh load lại nhiều lần
_parsers = {}


def get_parser(ext: str):
    """Trả về parser tương ứng với extension (nếu có hỗ trợ)."""
    lang_name = SUPPORTED_LANGS.get(ext.lower())
    if not lang_name:
        return None

    if ext not in _parsers:
        try:
            language = Language(LANGUAGE_SO_PATH, lang_name)
            parser = Parser()
            parser.set_language(language)
            _parsers[ext] = parser
        except Exception as e:
            print(f"⚠️ Không thể tạo parser cho {ext}: {e}")
            return None
    return _parsers[ext]


# =======================================
# 2️⃣ Hàm tách code theo function/class
# =======================================

def extract_functions_from_tree(source_code: str, parser) -> List[str]:
    """
    Dùng tree-sitter để tách các node function/class/method.
    """
    try:
        tree = parser.parse(bytes(source_code, "utf8"))
        root = tree.root_node

        chunks = []
        for node in root.children:
            if node.type in {
                "function_definition",
                "class_definition",
                "method_definition",
                "struct_specifier",
                "interface_declaration"
            }:
                start = node.start_byte
                end = node.end_byte
                chunk = source_code[start:end].strip()
                if chunk:
                    chunks.append(chunk)

        return chunks
    except Exception:
        return []


# =======================================
# 3️⃣ Fallback chia theo độ dài ký tự
# =======================================

def chunk_by_length(text: str, max_chunk_size: int = 3000) -> List[str]:
    """Fallback chia text theo độ dài ký tự."""
    return [text[i:i + max_chunk_size] for i in range(0, len(text), max_chunk_size)]


# =======================================
# 4️⃣ Hàm chính chunk_text
# =======================================

def chunk_text(source_code: str, ext: str = ".py", max_chunk_size: int = 3000) -> List[str]:
    """
    Chia code thành các phần logic theo function/class.
    Nếu không parse được -> fallback chia theo độ dài.
    """
    parser = get_parser(ext)
    if not parser:
        return chunk_by_length(source_code, max_chunk_size)

    chunks = extract_functions_from_tree(source_code, parser)

    if not chunks:
        return chunk_by_length(source_code, max_chunk_size)

    final_chunks = []
    for chunk in chunks:
        if len(chunk) > max_chunk_size:
            final_chunks.extend(chunk_by_length(chunk, max_chunk_size))
        else:
            final_chunks.append(chunk)
    return final_chunks


# =======================================
# 5️⃣ Test nhanh
# =======================================
if __name__ == "__main__":
    test_code = """
def foo():
    print("Hello")

class Bar:
    def baz(self, x):
        return x * 2
"""

    chunks = chunk_text(test_code, ext=".py")
    for i, c in enumerate(chunks, 1):
        print(f"----- CHUNK {i} -----\n{c}\n")
