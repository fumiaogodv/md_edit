from .. import config
from .path_util import safe_resolve


def read_file(relative_path: str) -> str:
    """读取文本文件内容，多编码降级（UTF-8 -> GBK -> UTF-8-SIG）。"""
    target = safe_resolve(relative_path)
    if not target.is_file():
        raise FileNotFoundError("文件不存在")

    for enc in ("utf-8", "gbk", "utf-8-sig", "latin-1"):
        try:
            return target.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("无法识别文件编码")


def read_raw_file(relative_path: str) -> bytes:
    """读取二进制文件（PDF、图片等）的原始字节。"""
    target = safe_resolve(relative_path)
    if not target.is_file():
        raise FileNotFoundError("文件不存在")
    return target.read_bytes()


def write_file(relative_path: str, content: str) -> None:
    """写回文件，仅允许可编辑扩展名。"""
    target = safe_resolve(relative_path)
    if target.suffix.lower() not in config.EDITABLE_EXTS:
        raise PermissionError("该文件类型不支持编辑")
    target.write_text(content, encoding="utf-8")
