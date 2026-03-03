"""知识库 API"""
import json
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select, func
from app.db.database import AsyncSessionLocal
from app.db.knowledge import KnowledgeBaseORM, KnowledgeDocumentORM, KnowledgeChunkORM
from app.services.kb_service import UPLOAD_DIR, extract_text, chunk_text, embed_texts

router = APIRouter()

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "image/jpeg": "image", "image/png": "image", "image/webp": "image",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "excel",
    "application/vnd.ms-excel": "excel",
}

TAG_CATEGORIES = {
    "行业": ["教育", "医疗", "金融", "科技", "法律", "制造", "零售"],
    "专业": ["计算机", "数学", "物理", "化学", "生物", "历史", "语文", "英语"],
    "学科": ["理科", "文科", "工科", "艺术"],
    "难度": ["入门", "初级", "中级", "高级"],
}


# ── 标签分类 ──────────────────────────────────────────────

@router.get("/tag-categories")
async def get_tag_categories():
    return TAG_CATEGORIES


# ── 知识库 CRUD ───────────────────────────────────────────

class KBCreate(BaseModel):
    name: str
    description: str = ""
    tags: list[dict] = []


@router.get("/bases")
async def list_bases():
    async with AsyncSessionLocal() as db:
        count_sub = (
            select(KnowledgeDocumentORM.kb_id, func.count().label("cnt"))
            .group_by(KnowledgeDocumentORM.kb_id)
            .subquery()
        )
        result = await db.execute(
            select(KnowledgeBaseORM, func.coalesce(count_sub.c.cnt, 0).label("doc_count"))
            .outerjoin(count_sub, KnowledgeBaseORM.id == count_sub.c.kb_id)
            .order_by(KnowledgeBaseORM.created_at.desc())
        )
        rows = result.all()
    return [{"id": b.id, "name": b.name, "description": b.description,
             "tags": json.loads(b.tags), "created_at": b.created_at,
             "doc_count": cnt} for b, cnt in rows]


@router.post("/bases")
async def create_base(body: KBCreate):
    async with AsyncSessionLocal() as db:
        kb = KnowledgeBaseORM(name=body.name, description=body.description,
                              tags=json.dumps(body.tags, ensure_ascii=False))
        db.add(kb)
        await db.commit()
        await db.refresh(kb)
    return {"id": kb.id, "name": kb.name, "description": kb.description,
            "tags": json.loads(kb.tags), "created_at": kb.created_at}


@router.put("/bases/{kb_id}")
async def update_base(kb_id: str, body: KBCreate):
    async with AsyncSessionLocal() as db:
        kb = await db.get(KnowledgeBaseORM, kb_id)
        if not kb:
            raise HTTPException(404, "知识库不存在")
        kb.name = body.name
        kb.description = body.description
        kb.tags = json.dumps(body.tags, ensure_ascii=False)
        await db.commit()
    return {"ok": True}


@router.delete("/bases/{kb_id}")
async def delete_base(kb_id: str):
    async with AsyncSessionLocal() as db:
        kb = await db.get(KnowledgeBaseORM, kb_id)
        if not kb:
            raise HTTPException(404, "知识库不存在")
        await db.delete(kb)
        await db.commit()
    return {"ok": True}


# ── 文档管理 ──────────────────────────────────────────────

@router.get("/bases/{kb_id}/documents")
async def list_documents(kb_id: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(KnowledgeDocumentORM)
            .where(KnowledgeDocumentORM.kb_id == kb_id)
            .order_by(KnowledgeDocumentORM.created_at.desc())
        )
        docs = result.scalars().all()
    return [{"id": d.id, "file_name": d.file_name, "file_type": d.file_type,
             "status": d.status, "chunk_count": d.chunk_count, "created_at": d.created_at}
            for d in docs]


async def _process_document(doc_id: str):
    """后台任务：解析文件 → 分块 → 向量化"""
    async with AsyncSessionLocal() as db:
        doc = await db.get(KnowledgeDocumentORM, doc_id)
        if not doc:
            return
        doc.status = "processing"
        await db.commit()

        try:
            text = extract_text(doc.file_path, doc.file_type)
            chunks = chunk_text(text)
            embeddings = await embed_texts(chunks)

            for i, (content, emb) in enumerate(zip(chunks, embeddings)):
                chunk = KnowledgeChunkORM(
                    doc_id=doc.id, kb_id=doc.kb_id, content=content,
                    chunk_index=i,
                    embedding=json.dumps(emb) if emb else None,
                )
                db.add(chunk)

            doc.chunk_count = len(chunks)
            doc.status = "done"
        except Exception as e:
            doc.status = "error"

        await db.commit()


@router.post("/bases/{kb_id}/upload")
async def upload_document(kb_id: str, background_tasks: BackgroundTasks,
                          file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"不支持的文件类型: {file.content_type}")

    async with AsyncSessionLocal() as db:
        kb = await db.get(KnowledgeBaseORM, kb_id)
        if not kb:
            raise HTTPException(404, "知识库不存在")

    doc_id = str(uuid.uuid4())
    kb_dir = UPLOAD_DIR / kb_id
    kb_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename).suffix
    file_path = kb_dir / f"{doc_id}{suffix}"
    file_path.write_bytes(await file.read())

    file_type = ALLOWED_TYPES[file.content_type]
    async with AsyncSessionLocal() as db:
        doc = KnowledgeDocumentORM(
            id=doc_id, kb_id=kb_id, file_name=file.filename,
            file_type=file_type, file_path=str(file_path),
        )
        db.add(doc)
        await db.commit()

    background_tasks.add_task(_process_document, doc_id)
    return {"id": doc_id, "file_name": file.filename, "file_type": file_type, "status": "pending"}


@router.delete("/bases/{kb_id}/documents/{doc_id}")
async def delete_document(kb_id: str, doc_id: str):
    async with AsyncSessionLocal() as db:
        doc = await db.get(KnowledgeDocumentORM, doc_id)
        if not doc or doc.kb_id != kb_id:
            raise HTTPException(404, "文档不存在")
        Path(doc.file_path).unlink(missing_ok=True)
        await db.delete(doc)
        await db.commit()
    return {"ok": True}


@router.get("/documents/{doc_id}/chunks")
async def get_chunks(doc_id: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(KnowledgeChunkORM)
            .where(KnowledgeChunkORM.doc_id == doc_id)
            .order_by(KnowledgeChunkORM.chunk_index)
        )
        chunks = result.scalars().all()
    return [{"id": c.id, "index": c.chunk_index, "content": c.content,
             "word_count": len(c.content)} for c in chunks]


# ── 预览 ──────────────────────────────────────────────────

@router.get("/documents/{doc_id}/preview")
async def preview_document(doc_id: str):
    async with AsyncSessionLocal() as db:
        doc = await db.get(KnowledgeDocumentORM, doc_id)
        if not doc:
            raise HTTPException(404, "文档不存在")

    path = Path(doc.file_path)
    if not path.exists():
        raise HTTPException(404, "文件不存在")

    if doc.file_type in ("pdf", "image"):
        return FileResponse(str(path))

    if doc.file_type == "excel":
        text = extract_text(doc.file_path, "excel")
        return {"content": text}

    raise HTTPException(400, "不支持预览此类型")


# ── 语义搜索 ──────────────────────────────────────────────

class SearchQuery(BaseModel):
    query: str
    top_k: int = 5


@router.post("/bases/{kb_id}/search")
async def search(kb_id: str, body: SearchQuery):
    from app.services.kb_service import search_chunks
    results = await search_chunks(kb_id, body.query, body.top_k, AsyncSessionLocal)
    return results
