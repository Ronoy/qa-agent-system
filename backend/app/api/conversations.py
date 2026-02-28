from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.db.database import get_db, ConversationORM, MessageORM
from app.models.schemas import Conversation, ConversationCreate, Message
from datetime import datetime
import uuid

router = APIRouter()


@router.get("", response_model=list[Conversation])
async def list_conversations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ConversationORM).order_by(ConversationORM.updated_at.desc())
    )
    convs = result.scalars().all()
    return [Conversation(
        id=c.id, title=c.title,
        created_at=c.created_at, updated_at=c.updated_at
    ) for c in convs]


@router.post("", response_model=Conversation)
async def create_conversation(body: ConversationCreate, db: AsyncSession = Depends(get_db)):
    conv = ConversationORM(id=str(uuid.uuid4()), title=body.title or "新对话")
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return Conversation(id=conv.id, title=conv.title,
                        created_at=conv.created_at, updated_at=conv.updated_at)


@router.get("/{conv_id}", response_model=Conversation)
async def get_conversation(conv_id: str, db: AsyncSession = Depends(get_db)):
    conv = await db.get(ConversationORM, conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="对话不存在")
    result = await db.execute(
        select(MessageORM).where(MessageORM.conversation_id == conv_id)
        .order_by(MessageORM.created_at)
    )
    msgs = result.scalars().all()
    return Conversation(
        id=conv.id, title=conv.title,
        created_at=conv.created_at, updated_at=conv.updated_at,
        messages=[Message(id=m.id, conversation_id=m.conversation_id,
                          role=m.role, content=m.content, created_at=m.created_at)
                  for m in msgs]
    )


@router.delete("/{conv_id}")
async def delete_conversation(conv_id: str, db: AsyncSession = Depends(get_db)):
    conv = await db.get(ConversationORM, conv_id)
    if not conv:
        raise HTTPException(status_code=404, detail="对话不存在")
    await db.delete(conv)
    await db.commit()
    return {"ok": True}
