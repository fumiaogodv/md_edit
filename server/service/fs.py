"""文件/文件夹的创建等文件系统操作。"""
from pathlib import Path

from .. import config
from .path_util import safe_resolve

# 名称里禁止出现的字符（防止路径穿越和非法文件名）
_FORBIDDEN_NAME_CHARS = ("/", "\\", ":", "*", "?", '"', "<", ">", "|")


def _clean_name(name: str) -> str:
    """清洗并校验新建文件/文件夹的名称。

    返回去除首尾空白后的合法名称；非法时抛 ValueError。
    """
    if not isinstance(name, str):
        raise ValueError("名称不能为空")
    name = name.strip()
    if not name:
        raise ValueError("名称不能为空")
    # 拒绝 . 开头（避免隐藏文件，如 .md-reader-progress.json 这类会被 IGNORE_PREFIXES 过滤）
    if name.startswith("."):
        raise ValueError("名称不能以 . 开头")
    # 拒绝 . 和 .. 等路径穿越
    if name in (".", ".."):
        raise ValueError("非法名称")
    # 拒绝包含非法字符
    for ch in _FORBIDDEN_NAME_CHARS:
        if ch in name:
            raise ValueError(f"名称不能包含字符：{ch}")
    return name


def _resolve_new_path(parent_path: str, name: str) -> Path:
    """把「父目录 + 名称」安全解析到挂载目录内的目标路径。"""
    parent = safe_resolve(parent_path)
    if not parent.is_dir():
        raise ValueError("父目录不存在或不是目录")
    target = parent / name
    # 再次确保在挂载目录内
    root = config.resolve_root()
    if root not in target.resolve().parents and target.resolve() != root:
        raise ValueError("非法路径：越出挂载目录")
    return target


def create_dir(parent_path: str, name: str) -> dict:
    """在 parent_path 下创建文件夹，返回新节点信息。"""
    name = _clean_name(name)
    target = _resolve_new_path(parent_path, name)
    if target.exists():
        raise ValueError("已存在同名文件或文件夹")
    target.mkdir()
    from .tree import to_node  # 局部导入避免循环依赖
    return to_node(target)


def create_file(parent_path: str, name: str, content: str = "") -> dict:
    """在 parent_path 下创建文件（仅允许可编辑扩展名），返回新节点信息。"""
    name = _clean_name(name)
    target = _resolve_new_path(parent_path, name)
    if target.suffix.lower() not in config.EDITABLE_EXTS:
        raise PermissionError("仅支持创建 Markdown/文本文件（.md/.markdown/.txt）")
    if target.exists():
        raise ValueError("已存在同名文件或文件夹")
    target.write_text(content, encoding="utf-8")
    from .tree import to_node  # 局部导入避免循环依赖
    return to_node(target)
