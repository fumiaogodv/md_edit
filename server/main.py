from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import config
from .service import file, search, tree

app = FastAPI(title="MD Reader", version="1.0.0")


class SaveBody(BaseModel):
    content: str


@app.get("/api/tree")
@app.get("/api/tree/{path:path}")
def get_tree(path: str = ""):
    try:
        return tree.list_dir(path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/file/{path:path}")
def get_file(path: str):
    try:
        content = file.read_file(path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"path": path, "content": content}


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
