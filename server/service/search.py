from pathlib import Path

from .. import config
from .path_util import to_rel_path


def search(keyword: str, limit_per_file: int = 10, ignore_case: bool = True) -> list[dict]:
    """全文搜索：遍历挂载目录下所有可搜索扩展名的文件，按行匹配。

    返回命中文件及其匹配行。
    """
    if not keyword:
        return []

    root = config.resolve_root()
    kw = keyword.lower() if ignore_case else keyword

    results = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in config.SEARCHABLE_EXTS:
            continue
        if p.name.startswith(config.IGNORE_PREFIXES):
            continue

        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                text = p.read_text(encoding="gbk")
            except (UnicodeDecodeError, OSError):
                continue
        except OSError:
            continue

        matches = []
        for i, line in enumerate(text.splitlines(), 1):
            hay = line.lower() if ignore_case else line
            if kw in hay:
                matches.append({"line": i, "text": line.strip()[:200]})
                if len(matches) >= limit_per_file:
                    break

        if matches:
            results.append({
                "path": to_rel_path(p),
                "name": p.name,
                "matches": matches,
            })

    return results
