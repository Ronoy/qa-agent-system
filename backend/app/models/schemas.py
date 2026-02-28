from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from enum import Enum


class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"
    tool = "tool"


class Message(BaseModel):
    id: Optional[int] = None
    conversation_id: Optional[str] = None
    role: MessageRole
    content: str
    created_at: Optional[datetime] = None


class Conversation(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[Message]] = None


class ConversationCreate(BaseModel):
    title: Optional[str] = "新对话"


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str


class ChatStreamEvent(BaseModel):
    type: str  # "text" | "tool_call" | "tool_result" | "done" | "error"
    content: Optional[str] = None
    tool_name: Optional[str] = None
    tool_args: Optional[dict] = None
