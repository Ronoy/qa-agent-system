"""知识库语义检索技能"""
from app.skills.base import Skill, SkillResult


class KnowledgeSearchSkill(Skill):
    name = "search_knowledge_base"
    description = "在指定知识库中语义检索相关内容，用于回答基于本地文档的问题"
    version = "1.0.0"
    tags = ["知识库", "检索"]
    parameters = {
        "type": "object",
        "properties": {
            "kb_id": {"type": "string", "description": "知识库ID"},
            "query": {"type": "string", "description": "检索查询语句"},
            "top_k": {"type": "integer", "description": "返回结果数量，默认5", "default": 5},
        },
        "required": ["kb_id", "query"]
    }

    async def execute(self, kb_id: str, query: str, top_k: int = 5, **kwargs) -> SkillResult:
        try:
            from app.db.database import AsyncSessionLocal
            from app.services.kb_service import search_chunks
            results = await search_chunks(kb_id, query, top_k, AsyncSessionLocal)
            if not results:
                return SkillResult(success=True, data={"results": [], "message": "未找到相关内容"})
            return SkillResult(success=True, data={"results": results}, metadata={"count": len(results)})
        except Exception as e:
            return SkillResult(success=False, data=None, error=str(e))
