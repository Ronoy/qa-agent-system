from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
import json
import uuid
from datetime import datetime

from app.db.database import AsyncSessionLocal, ConversationORM, MessageORM, AttachmentORM
from app.models.schemas import ChatRequest
from app.agent.agent import run_agent_stream

router = APIRouter()


async def _load_attachments(attachment_ids: list[str]) -> list[dict]:
    """加载附件数据"""
    attachments = []
    async with AsyncSessionLocal() as db:
        for att_id in attachment_ids:
            att = await db.get(AttachmentORM, att_id)
            if att:
                attachments.append({
                    "file_name": att.file_name,
                    "file_type": att.file_type,
                    "extracted_text": att.extracted_text or "",
                })
    return attachments


@router.post("/stream")
async def chat_stream(req: ChatRequest):
    # 在生成器外先处理对话创建和历史加载
    async with AsyncSessionLocal() as db:
        conv_id = req.conversation_id
        if conv_id:
            conv = await db.get(ConversationORM, conv_id)
            if not conv:
                raise HTTPException(status_code=404, detail="对话不存在")
        else:
            conv_id = str(uuid.uuid4())
            title = req.message[:20] + ("..." if len(req.message) > 20 else "")
            conv = ConversationORM(id=conv_id, title=title)
            db.add(conv)
            await db.commit()

        result = await db.execute(
            select(MessageORM)
            .where(MessageORM.conversation_id == conv_id)
            .order_by(MessageORM.created_at)
        )
        history_orm = result.scalars().all()
        history = [{"role": m.role, "content": m.content} for m in history_orm]

        # 保存用户消息
        user_msg = MessageORM(conversation_id=conv_id, role="user", content=req.message)
        db.add(user_msg)
        await db.commit()

    async def event_generator():
        yield f"data: {json.dumps({'type': 'conversation_id', 'content': conv_id}, ensure_ascii=False)}\n\n"

        # 加载附件
        attachments = []
        if req.attachment_ids:
            attachments = await _load_attachments(req.attachment_ids)

        full_response = []
        async for event in run_agent_stream(req.message, history, attachments, req.kb_ids, req.model):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
            if event["type"] == "text":
                full_response.append(event["content"])

        # 用独立 session 保存 assistant 回复
        if full_response:
            assistant_content = "".join(full_response)
            async with AsyncSessionLocal() as db2:
                ai_msg = MessageORM(
                    conversation_id=conv_id,
                    role="assistant",
                    content=assistant_content
                )
                db2.add(ai_msg)
                conv_update = await db2.get(ConversationORM, conv_id)
                if conv_update:
                    conv_update.updated_at = datetime.utcnow()
                await db2.commit()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )
