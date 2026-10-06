from pathlib import Path

from .. import config


def safe_resolve(relative_path: str) -> Path:
    """把相对路径安全解析到 ROOT_DIR 内部，越界则抛 ValueError。

    防止路径穿越（如 ../、../../etc/passwd）。
    """
    root = config.resolve_root()
    # 规范化：去空、替换反斜杠、剥离开头斜杠
    rel = (relative_path or "").strip().replace("\\", "/").lstrip("/")
    target = (root / rel).resolve()

    # 必须是 root 本身或 root 的子路径
    if target != root and root not in target.parents:
        raise ValueError("非法路径：越出挂载目录")

    return target


def to_rel_path(p: Path) -> str:
    """绝对路径 -> 相对于 ROOT_DIR 的正斜杠相对路径。"""
    root = config.resolve_root()
    return str(p.relative_to(root)).replace("\\", "/")
