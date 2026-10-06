from pathlib import Path

from .. import config
from .path_util import safe_resolve, to_rel_path


def _node(p: Path) -> dict:
    """把文件/目录 Path 转成前端可用的节点结构。"""
    is_dir = p.is_dir()
    return {
        "name": p.name,
        "type": "dir" if is_dir else "file",
        "path": to_rel_path(p),
        "ext": ("" if is_dir else p.suffix.lower()),
        "size": (0 if is_dir else p.stat().st_size),
        "editable": (not is_dir) and p.suffix.lower() in config.EDITABLE_EXTS,
    }


def list_dir(relative_path: str = "") -> list[dict]:
    """返回某目录下的直接子项（懒加载，不递归）。"""
    target = safe_resolve(relative_path)
    if not target.is_dir():
        raise ValueError("路径不是目录")

    items = []
    for p in target.iterdir():
        if p.name.startswith(config.IGNORE_PREFIXES):
            continue
        try:
            items.append(_node(p))
        except OSError:
            continue

    # 排序：目录在前、文件在后；同类按名称（忽略大小写）
    items.sort(key=lambda x: (x["type"] != "dir", x["name"].lower()))
    return items
