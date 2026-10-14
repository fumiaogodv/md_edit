from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import config
from .service import file, fs, progress, search, tree

app = FastAPI(title="MD Reader", version="1.0.0")


class SaveBody(BaseModel):
    content: str


class ProgressBody(BaseModel):
    entry: dict


class CreateBody(BaseModel):
    name: str
    content: str = ""


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


@app.post("/api/tree/{path:path}")
def create_dir(path: str, body: CreateBody):
    """在 path 目录下创建子文件夹。"""
    try:
        return fs.create_dir(path, body.name)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/file/{path:path}")
def create_file(path: str, body: CreateBody):
    """在 path 目录下创建文件（仅 .md/.markdown/.txt）。"""
    try:
        return fs.create_file(path, body.name, body.content)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/file/raw/{path:path}")
def get_raw_file(path: str, request: Request, response: Response):
    """返回二进制文件（PDF/图片）的原始字节，支持 ETag 条件请求缓存。"""
    try:
        etag = file.file_etag(path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "no-cache"
    if request.headers.get("If-None-Match") == etag:
        response.status_code = 304
        return response

    try:
        data = file.read_raw_file(path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    suffix = Path(path).suffix.lower()
    mime = _MIME_TYPES.get(suffix, "application/octet-stream")
    return Response(content=data, media_type=mime, headers={"ETag": etag, "Cache-Control": "no-cache"})


@app.get("/api/file/{path:path}")
def get_file(path: str, request: Request, response: Response):
    try:
        etag = file.file_etag(path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "no-cache"
    if request.headers.get("If-None-Match") == etag:
        response.status_code = 304
        return response

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


# 前端静态托管 + SPA fallback
# 前端用 history 路由（网址直接拼文件路径，如 /数据结构/3图/总文件.md），
# 刷新时任意非 /api 路径都要返回 index.html，交给前端路由还原状态。
_static = Path(config.STATIC_DIR)
if _static.is_dir():
    _index = _static / "index.html"

    # 先挂载静态资源目录（assets/ 等），命中真实文件就返回
    app.mount("/assets", StaticFiles(directory=str(_static / "assets")), name="assets")

    # catch-all：所有未命中的路径（含根路径）都返回 index.html
    @app.get("/{full_path:path}")
    def spa_fallback(full_path: str):
        if _index.is_file():
            return FileResponse(_index)
        return {"detail": "前端资源未构建"}

