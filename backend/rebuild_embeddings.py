"""重新生成所有文档的 embedding"""
import asyncio
import json
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.knowledge import KnowledgeDocumentORM, KnowledgeChunkORM
from app.services.kb_service import extract_text, chunk_text, embed_texts

async def rebuild():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(KnowledgeDocumentORM))
        docs = result.scalars().all()

        for doc in docs:
            print(f"处理: {doc.file_name}")

            # 删除旧 chunks
            await db.execute(
                KnowledgeChunkORM.__table__.delete().where(KnowledgeChunkORM.doc_id == doc.id)
            )

            # 重新生成
            text = extract_text(doc.file_path, doc.file_type)
            chunks = chunk_text(text)
            embeddings = await embed_texts(chunks)

            for i, (content, emb) in enumerate(zip(chunks, embeddings)):
                chunk = KnowledgeChunkORM(
                    doc_id=doc.id, kb_id=doc.kb_id, content=content,
                    chunk_index=i, embedding=json.dumps(emb) if emb else None
                )
                db.add(chunk)

            doc.chunk_count = len(chunks)
            print(f"  生成 {len(chunks)} 个块，{sum(1 for e in embeddings if e)} 个有向量")

        await db.commit()
        print("完成！")

if __name__ == "__main__":
    asyncio.run(rebuild())
