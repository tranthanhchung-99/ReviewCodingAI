# utils/chunk_utils.py
from tree_sitter import Parser
from tree_sitter_languages import get_language, get_parser

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
    ".html": "html",
    ".css": "css",
    ".json": "json",
    ".lua": "lua",
    ".rb": "ruby",
    ".sql": "sql",
    ".md": "markdown",
    ".xml": "xml",
    ".yaml": "yaml",
    ".toml": "toml",
    ".sh": "bash",
    ".r": "r",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
    ".dart": "dart",
}

def chunk_text(code: str, ext: str, max_chunk_size: int = 3000):
    """
    Chia code thành các 'chunk' nhỏ theo hàm, lớp hoặc khối logic.
    Hỗ trợ tree-sitter đa ngôn ngữ.
    """
    lang_name = SUPPORTED_LANGS.get(ext)
    if not lang_name:
        raise ValueError(f"❌ Không hỗ trợ extension '{ext}' — hỗ trợ: {list(SUPPORTED_LANGS.keys())}")

    try:
        # ✅ Lấy ngôn ngữ & parser đúng API mới
        language = get_language(lang_name)
        parser = Parser()
        parser.set_language(language)

        tree = parser.parse(bytes(code, "utf8"))
        root = tree.root_node

        chunks = []
        for node in root.children:
            if node.type in (
                    "function_definition", "class_definition", "method_definition",
                    "function_declaration", "class_declaration"
            ):
                snippet = code[node.start_byte:node.end_byte]
                if len(snippet) > max_chunk_size:
                    for i in range(0, len(snippet), max_chunk_size):
                        chunks.append(snippet[i:i+max_chunk_size])
                else:
                    chunks.append(snippet.strip())

        # fallback nếu không có node cấu trúc
        if not chunks:
            lines = code.strip().split("\n")
            for i in range(0, len(lines), 30):
                chunks.append("\n".join(lines[i:i+30]))

        return chunks

    except Exception as e:
        print(f"⚠️ Tree-sitter lỗi ({lang_name}): {e} → fallback chia theo dòng.")
        lines = code.strip().split("\n")
        return ["\n".join(lines[i:i+30]) for i in range(0, len(lines), 30)]
