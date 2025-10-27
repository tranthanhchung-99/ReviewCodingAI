"""
utils/build_languages.py
------------------------
Tự động:
- Clone các repo tree-sitter phổ biến (40+ ngôn ngữ)
- Build file `build/my-languages.so` để dùng trong `chunk_utils.py`
- An toàn, bỏ qua repo lỗi mà không dừng toàn bộ quá trình
"""

import os
import subprocess
from tree_sitter import Language

# ==============================
# 1️⃣ Cấu hình
# ==============================
BASE_DIR = os.path.join(os.getcwd(), "tree_sitter_langs")
BUILD_DIR = os.path.join(os.getcwd(), "build")
LIB_PATH = os.path.join(BUILD_DIR, "my-languages.so")

# Danh sách ngôn ngữ phổ biến
REPOS = {
    "tree-sitter-python": "https://github.com/tree-sitter/tree-sitter-python.git",
    "tree-sitter-javascript": "https://github.com/tree-sitter/tree-sitter-javascript.git",
    "tree-sitter-typescript": "https://github.com/tree-sitter/tree-sitter-typescript.git",
    "tree-sitter-java": "https://github.com/tree-sitter/tree-sitter-java.git",
    "tree-sitter-c": "https://github.com/tree-sitter/tree-sitter-c.git",
    "tree-sitter-cpp": "https://github.com/tree-sitter/tree-sitter-cpp.git",
    "tree-sitter-c-sharp": "https://github.com/tree-sitter/tree-sitter-c-sharp.git",
    "tree-sitter-go": "https://github.com/tree-sitter/tree-sitter-go.git",
    "tree-sitter-rust": "https://github.com/tree-sitter/tree-sitter-rust.git",
    "tree-sitter-php": "https://github.com/tree-sitter/tree-sitter-php.git",
    "tree-sitter-ruby": "https://github.com/tree-sitter/tree-sitter-ruby.git",
    "tree-sitter-lua": "https://github.com/tree-sitter/tree-sitter-lua.git",
    "tree-sitter-json": "https://github.com/tree-sitter/tree-sitter-json.git",
    "tree-sitter-html": "https://github.com/tree-sitter/tree-sitter-html.git",
    "tree-sitter-css": "https://github.com/tree-sitter/tree-sitter-css.git",
    "tree-sitter-sql": "https://github.com/m-novikov/tree-sitter-sql.git",
    "tree-sitter-markdown": "https://github.com/MDeiml/tree-sitter-markdown.git",
    "tree-sitter-bash": "https://github.com/tree-sitter/tree-sitter-bash.git",
    "tree-sitter-perl": "https://github.com/ganezdragon/tree-sitter-perl.git",
    "tree-sitter-kotlin": "https://github.com/fwcd/tree-sitter-kotlin.git",
    "tree-sitter-swift": "https://github.com/alex-pinkus/tree-sitter-swift.git",
    "tree-sitter-scala": "https://github.com/tree-sitter/tree-sitter-scala.git",
    "tree-sitter-dart": "https://github.com/UserNobody14/tree-sitter-dart.git",
    "tree-sitter-r": "https://github.com/r-lib/tree-sitter-r.git",
    "tree-sitter-haskell": "https://github.com/tree-sitter/tree-sitter-haskell.git",
    "tree-sitter-yaml": "https://github.com/ikatyang/tree-sitter-yaml.git",
    "tree-sitter-toml": "https://github.com/ikatyang/tree-sitter-toml.git",
    "tree-sitter-xml": "https://github.com/tree-sitter/tree-sitter-xml.git",
    "tree-sitter-vue": "https://github.com/ikatyang/tree-sitter-vue.git",
    "tree-sitter-svelte": "https://github.com/Himujjal/tree-sitter-svelte.git",
    "tree-sitter-json5": "https://github.com/Joakker/tree-sitter-json5.git",
    "tree-sitter-dockerfile": "https://github.com/camdencheek/tree-sitter-dockerfile.git",
    "tree-sitter-graphql": "https://github.com/bkegley/tree-sitter-graphql.git",
    "tree-sitter-ini": "https://github.com/justinmk/tree-sitter-ini.git",
    "tree-sitter-elixir": "https://github.com/elixir-lang/tree-sitter-elixir.git",
    "tree-sitter-erlang": "https://github.com/the-mikedavis/tree-sitter-erlang.git",
    "tree-sitter-nim": "https://github.com/alaviss/tree-sitter-nim.git",
    "tree-sitter-zig": "https://github.com/maxxnino/tree-sitter-zig.git",
}

# ==============================
# 2️⃣ Clone repo
# ==============================
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(BUILD_DIR, exist_ok=True)

print("📦 Bắt đầu clone/cập nhật ngôn ngữ Tree-sitter...\n")

for name, url in REPOS.items():
    repo_path = os.path.join(BASE_DIR, name)
    if not os.path.exists(repo_path):
        print(f"🌱 Cloning {name} ...")
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", url, repo_path],
                check=True, capture_output=True
            )
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Lỗi khi clone {name}: {e}")
    else:
        print(f"✅ {name} đã tồn tại, bỏ qua clone.")

# ==============================
# 3️⃣ Build thư viện .so
# ==============================
print("\n🔧 Đang build thư viện Tree-sitter đa ngôn ngữ...\n")

try:
    Language.build_library(
        LIB_PATH,
        [os.path.join(BASE_DIR, name) for name in REPOS.keys() if os.path.exists(os.path.join(BASE_DIR, name))]
    )
    print(f"\n✅ Build thành công! File sinh ra: {LIB_PATH}")
except Exception as e:
    print(f"\n❌ Lỗi build: {e}")
    print("👉 Gợi ý: Kiểm tra xem bạn có cài đầy đủ 'gcc' hoặc 'build-essential' chưa.")
