# ===== 阶段1：构建前端 =====
FROM node:20-alpine AS webbuild
WORKDIR /app/web

# 先复制依赖清单，利用 Docker 层缓存
COPY web/package.json web/package-lock.json* ./
RUN npm install --registry=https://registry.npmmirror.com

# 复制源码并构建
COPY web/ ./
RUN npm run build

# ===== 阶段2：运行后端 + 托管前端产物 =====
FROM python:3.11-slim

WORKDIR /app

# 安装 Python 依赖
COPY server/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制后端代码
COPY server/ ./server/

# 注入前端构建产物
COPY --from=webbuild /app/web/dist ./static

ENV ROOT_DIR=/data \
    PORT=8000 \
    STATIC_DIR=/app/static

EXPOSE 8000

CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
