import os
from pathlib import Path

# 挂载根目录（对应 docker 的 -v 挂载点）
ROOT_DIR = os.environ.get("ROOT_DIR", "/data")

# 服务配置
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))

# 允许编辑的文件扩展名（只有这些可以打开编辑/保存）
EDITABLE_EXTS = {".md", ".markdown", ".txt"}

# 搜索时扫描的扩展名
SEARCHABLE_EXTS = {".md", ".markdown", ".txt"}

# 可在阅读器中打开（渲染/预览）的扩展名（含只读类型）
READABLE_EXTS = {
    ".md", ".markdown", ".txt",   # 文本
    ".pdf",                        # PDF
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".ico",  # 图片
}

# 进度记录文件名（存放在挂载根目录下，隐藏文件）
PROGRESS_FILE = ".md-reader-progress.json"

# 隐藏文件/目录前缀（跳过）
IGNORE_PREFIXES = (".",)

# 前端静态资源目录（Docker 构建时注入）
STATIC_DIR = Path(os.environ.get("STATIC_DIR", "static"))


def resolve_root() -> Path:
    return Path(ROOT_DIR).resolve()
