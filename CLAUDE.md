# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概述

这是一个智能问答智能体系统，采用 FastAPI 后端 + Vue 3 前端架构。系统通过 AI 智能体提供教育辅助功能，可以访问学生数据、执行网络搜索、求解数学问题，并生成个性化学习建议。

## 架构说明

### 后端 (Python/FastAPI)
- **入口文件**: `backend/app/main.py` - FastAPI 应用，配置了 CORS 中间件
- **智能体系统**: `backend/app/agent/agent.py` - 主智能体循环，支持工具调用
  - 使用 OpenAI 兼容 API（默认为 DeepSeek）
  - 先非流式执行工具调用，再流式输出文本响应
  - 最多 5 轮工具调用迭代，防止死循环
- **工具集**: `backend/app/agent/tools.py` - 10 个函数调用工具，包括：
  - 学生数据查询（考勤、学习状态、任务、知识点掌握度）
  - 通过 DuckDuckGo 进行网络搜索
  - 通过 SymPy 求解数学问题
  - 生成练习题、制定学习计划、讲解知识点
- **数据库**: SQLite + 异步 SQLAlchemy (aiosqlite)
  - `backend/app/db/database.py` 中定义 `ConversationORM` 和 `MessageORM` 模型
  - 通过 lifespan 上下文管理器在应用启动时初始化数据库
- **API 路由**:
  - `/api/chat/stream` - 服务器发送事件 (SSE) 流式聊天端点
  - `/api/conversations` - 对话 CRUD 操作
  - `/api/data` - 模拟学生数据端点

### 前端 (Vue 3/TypeScript)
- **构建工具**: Vite
- **状态管理**: Pinia，store 位于 `frontend/src/stores/`
- **组件**: Vue 单文件组件位于 `frontend/src/components/`
  - 聊天界面，支持 Markdown 渲染（markdown-it + KaTeX 数学公式）
  - 侧边栏对话列表
  - 基于 SSE 的流式消息显示

## 开发命令

### 后端
```bash
# 启动后端（自动创建 venv、安装依赖、运行 uvicorn）
./start_backend.sh

# 或手动执行：
cd backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**环境配置**: 复制 `backend/.env.example` 为 `backend/.env`，并设置 `DEEPSEEK_API_KEY`

### 前端
```bash
# 启动前端开发服务器
./start_frontend.sh

# 或手动执行：
cd frontend
npm install
npm run dev
```

### 构建
```bash
cd frontend
npm run build  # TypeScript 编译 + Vite 构建
```

## 关键配置

- **API 凭证**: `backend/app/config.py` 从 `.env` 加载
  - `DEEPSEEK_API_KEY` - 智能体功能必需
  - `DEEPSEEK_BASE_URL` - 默认: https://api.deepseek.com
  - `DEEPSEEK_MODEL` - 默认: deepseek-chat
  - `DATABASE_URL` - 默认: sqlite+aiosqlite:///./qa_agent.db
  - `CORS_ORIGINS` - 默认: http://localhost:5173

- **系统提示词**: `backend/app/agent/prompts.py` 定义智能体行为

## 重要模式

### 智能体工具调用流程
1. 用户消息追加到对话历史
2. 非流式 API 调用，启用工具
3. 如有工具调用：执行工具、注入结果、重复（最多 5 轮）
4. 最终流式生成响应，不使用工具
5. 流式完成后将助手消息保存到数据库

### 数据库会话
- 对独立操作使用单独的 `AsyncSessionLocal()` 上下文
- 聊天端点使用一个会话进行初始设置，使用另一个会话保存最终响应
- 避免长时间流式操作期间的会话冲突

### SSE 事件格式
事件以 `data: {JSON}\n\n` 格式 yield，类型包括：
- `conversation_id` - 创建新对话
- `tool_call` - 调用工具，包含名称和参数
- `tool_result` - 工具执行结果
- `text` - 流式响应片段
- `done` - 流式完成

## 测试

目前不存在测试套件。添加测试时，使用 pytest + pytest-asyncio 测试异步端点。
