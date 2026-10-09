"""阅读进度持久化。

进度存放在挂载根目录下的隐藏文件 `.md-reader-progress.json`，结构：
{
  "<相对路径>": {
    "type": "md" | "pdf",
    "anchor": "标题文本" | null,   # md 用标题锚点
    "scroll": 0.0,                 # md 退化用：滚动比例 0~1
    "page": 1,                     # pdf 用：页码
    "updatedAt": 1759999999
  }
}
"""
import json
import os
import threading

from .. import config
from .path_util import safe_resolve

# 单进程内的写锁，避免并发写坏文件
_lock = threading.Lock()


def _progress_path():
    root = config.resolve_root()
    return root / config.PROGRESS_FILE


def load_all() -> dict:
    """读取全部进度，文件不存在返回空 dict。"""
    p = _progress_path()
    if not p.is_file():
        return {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def get(relative_path: str) -> dict | None:
    """读取单个文件的进度，无记录返回 None。"""
    return load_all().get(relative_path)


def save(relative_path: str, entry: dict) -> None:
    """保存某文件的进度（合并写回，原子写防损坏）。"""
    # 规范化相对路径
    rel = (relative_path or "").strip().replace("\\", "/").lstrip("/")

    with _lock:
        data = load_all()
        data[rel] = entry
        p = _progress_path()
        tmp = p.with_suffix(".tmp")
        # 原子写：先写临时文件再替换
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, p)
