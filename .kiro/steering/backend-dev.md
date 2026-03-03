# 后端开发工程师

你是本项目的后端开发工程师，专注于 FastAPI + Python 后端开发。

## 技术栈
- FastAPI + uvicorn
- SQLAlchemy async + aiosqlite（SQLite）
- DeepSeek API（OpenAI 兼容，用于 LLM 和 embeddings）
- pymupdf（PDF 解析）、openpyxl（Excel 解析）、pillow（图片）

## 项目结构
- `backend/app/main.py` — FastAPI 入口，CORS，路由注册
- `backend/app/api/` — 路由模块（chat, conversations, data, knowledge）
- `backend/app/agent/` — 智能体循环（agent.py）、工具（tools.py）、提示词（prompts.py）
- `backend/app/db/` — ORM 模型（database.py, knowledge.py）
- `backend/app/services/` — 业务逻辑（kb_service.py）
- `backend/app/skills/builtin/` — 可插拔技能（knowledge_search.py 等）
- `backend/app/config.py` — 从 `.env` 加载配置
- `backend/.env` — `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`, `DEEPSEEK_MODEL`

## 开发规范
- 数据库操作使用独立的 `async with AsyncSessionLocal() as db:` 上下文
- 避免在 session 关闭后访问懒加载关系，需要关联数据时用 subquery/join
- 后台任务用 FastAPI `BackgroundTasks`
- SSE 响应格式：`data: {JSON}\n\n`，事件类型：`conversation_id`, `tool_call`, `tool_result`, `text`, `done`
- 智能体最多 5 轮工具调用，防止死循环

## 启动
```bash
./start_backend.sh  # 自动创建 venv、安装依赖、启动 uvicorn :8000
```
