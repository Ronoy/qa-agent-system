"""知识库文件解析、分块、向量化服务"""
import json
import math
from pathlib import Path
from typing import Optional
from openai import AsyncOpenAI
from app.config import ZHIPU_API_KEY, ZHIPU_BASE_URL

UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads" / "knowledge"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

_embed_client = AsyncOpenAI(api_key=ZHIPU_API_KEY, base_url=ZHIPU_BASE_URL)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


# ── 文本提取 ──────────────────────────────────────────────

def extract_pdf(path: Path) -> str:
    try:
        import fitz
        doc = fitz.open(str(path))
        text = "\n".join(p.get_text() for p in doc)
        doc.close()
        return text
    except Exception as e:
        return f"PDF解析失败: {e}"


def extract_excel(path: Path) -> str:
    try:
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        lines = []
        for sheet in wb.worksheets:
            lines.append(f"[Sheet: {sheet.title}]")
            for row in sheet.iter_rows(values_only=True):
                row_text = "\t".join(str(c) if c is not None else "" for c in row)
                if row_text.strip():
                    lines.append(row_text)
        return "\n".join(lines)
    except Exception as e:
        return f"Excel解析失败: {e}"


def extract_image(path: Path) -> str:
    try:
        from PIL import Image
        import pytesseract
        img = Image.open(str(path))
        text = pytesseract.image_to_string(img, lang='chi_sim+eng')
        return text.strip() or f"[图片无文字内容: {path.name}]"
    except Exception as e:
        return f"[图片OCR失败: {e}]"


def extract_text(file_path: str, file_type: str) -> str:
    path = Path(file_path)
    if file_type == "pdf":
        return extract_pdf(path)
    elif file_type == "excel":
        return extract_excel(path)
    else:  # image
        return extract_image(path)


# ── 分块 ─────────────────────────────────────────────────

def chunk_text(text: str) -> list[str]:
    if not text.strip():
        return []
    chunks, start = [], 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return [c for c in chunks if c.strip()]


# ── 向量化 ────────────────────────────────────────────────

async def embed_texts(texts: list[str]) -> list[Optional[list[float]]]:
    """批量获取 embedding，智谱限制每次最多 64 条"""
    results = []
    batch_size = 60

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        try:
            resp = await _embed_client.embeddings.create(
                model="embedding-3",
                input=batch,
            )
            results.extend([item.embedding for item in resp.data])
        except Exception as e:
            print(f"Embedding 失败 (batch {i//batch_size + 1}): {e}")
            results.extend([None] * len(batch))

    return results


# ── 相似度搜索 ────────────────────────────────────────────

def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


async def search_chunks(kb_id: str, query: str, top_k: int = 5, db=None) -> list[dict]:
    from sqlalchemy import select
    from app.db.knowledge import KnowledgeChunkORM

    q_emb = (await embed_texts([query]))[0]

    async with db() as session:
        result = await session.execute(
            select(KnowledgeChunkORM).where(KnowledgeChunkORM.kb_id == kb_id)
        )
        chunks = result.scalars().all()

    scored = []
    for c in chunks:
        if c.embedding and q_emb:
            emb = json.loads(c.embedding)
            score = cosine_similarity(q_emb, emb)
        else:
            score = 0.0
        scored.append({"id": c.id, "content": c.content, "score": score, "doc_id": c.doc_id})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return [r for r in scored[:top_k] if r["score"] >= 0.3]
