from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import config
from .service import file, progress, search, tree

app = FastAPI(title="MD Reader", version="1.0.0")


class SaveBody(BaseModel):
    content: str


class ProgressBody(BaseModel):
    entry: dict


# 二进制文件的 MIME 类型映射（用于 /api/file/raw 返回正确的 Content-Type）
_MIME_TYPES = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
    ".bmp": "image/bmp",
    ".ico": "image/x-icon",
}


@app.get("/api/tree")
@app.get("/api/tree/{path:path}")
def get_tree(path: str = ""):
    try:
        return tree.list_dir(path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/file/raw/{path:path}")
def get_raw_file(path: str):
    """返回二进制文件（PDF/图片）的原始字节。"""
    try:
        data = file.read_raw_file(path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    suffix = Path(path).suffix.lower()
    mime = _MIME_TYPES.get(suffix, "application/octet-stream")
    return Response(content=data, media_type=mime)


@app.get("/api/file/{path:path}")
def get_file(path: str):
    try:
        content = file.read_file(path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"path": path, "content": content}


@app.get("/api/progress/{path:path}")
def get_progress(path: str):
    """读取某文件的阅读进度。"""
    entry = progress.get(path)
    return {"path": path, "entry": entry}


@app.put("/api/progress/{path:path}")
@app.post("/api/progress/{path:path}")
def put_progress(path: str, body: ProgressBody):
    """保存某文件的阅读进度（POST 用于 sendBeacon 场景）。"""
    progress.save(path, body.entry)
    return {"ok": True}


@app.put("/api/file/{path:path}")
def put_file(path: str, body: SaveBody):
    try:
        file.write_file(path, body.content)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True}


@app.get("/api/search")
def do_search(q: str = ""):
    return {"query": q, "results": search.search(q)}


# 前端静态托管（放在最后，避免吞掉 /api 路由）
_static = Path(config.STATIC_DIR)
if _static.is_dir():
    app.mount("/", StaticFiles(directory=str(_static), html=True), name="static")
