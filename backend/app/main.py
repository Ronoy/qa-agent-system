from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import CORS_ORIGINS
from app.db.database import init_db
from app.api import chat, conversations, data, skills, upload, knowledge
from app.agent.agent import initialize_skills


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化数据库
    await init_db()
    # 初始化 Skills 系统
    await initialize_skills()
    yield


app = FastAPI(title="智能问答智能体系统", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])
app.include_router(data.router, prefix="/api/data", tags=["data"])
app.include_router(skills.router, prefix="/api/skills", tags=["skills"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])


@app.get("/")
async def root():
    return {"status": "ok", "message": "智能问答智能体系统运行中 (Skills 系统已启用)"}
