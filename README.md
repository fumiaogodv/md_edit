# MD Reader

一个本地 Markdown 阅读器，支持文件夹分类导航、标题大纲跳转、全文搜索、轻量编辑。以 Docker 镜像交付，跨设备运行。

## 功能

- 📁 文件夹分类树（懒加载，可折叠）
- 📄 点击展示 Markdown 内容（代码高亮 + 表格 + 数学公式）
- 📑 一、二级标题大纲跳转（平滑滚动）
- 🔍 全文搜索（按文件内容搜索，支持定位）
- ✏️ 轻量编辑（编辑/预览切换，保存写回磁盘）
- 📃 非 md 文件也展示（仅 md/markdown/txt 可打开编辑）

## 快速开始

### 方式一：Docker（推荐）

```bash
# 1. 构建镜像
docker build -t md-reader .

# 2. 运行（把 D:/notes 换成你的 Markdown 目录）
docker run -d -p 8000:8000 -v D:/notes:/data --name md-reader md-reader

# 3. 浏览器访问
# http://localhost:8000
```

### 方式二：docker compose

编辑 `docker-compose.yml`，把 `D:/notes:/data` 改成你的目录，然后：

```bash
docker compose up -d
```

### 方式三：本地开发

```bash
# 后端
cd server
pip install -r requirements.txt
ROOT_DIR=/你的/md目录 uvicorn main:app --reload --port 8000

# 前端（另开终端）
cd web
npm install
npm run dev
# 访问 http://localhost:5173
```

## 配置

通过环境变量配置：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `ROOT_DIR` | `/data` | Markdown 文件挂载根目录 |
| `PORT` | `8000` | 服务端口 |
| `STATIC_DIR` | `static` | 前端静态资源目录 |

## 技术栈

- 后端：Python 3.11 + FastAPI + Uvicorn
- 前端：Vue 3 + Vite + Naive UI
- 渲染：markdown-it + highlight.js + KaTeX
- 编辑：CodeMirror 6

## 目录结构

```
md-reader/
├── server/          # Python 后端
├── web/             # Vue3 前端
├── Dockerfile       # 多阶段构建
├── docker-compose.yml
└── README.md
```
