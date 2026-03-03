"""
网络搜索技能
"""
import asyncio
from app.skills.base import Skill, SkillResult


class WebSearchSkill(Skill):
    """联网搜索最新信息"""

    name = "web_search"
    description = "联网搜索最新信息，适用于查询时事、政策、考试资讯、学科前沿知识等实时内容"
    version = "1.0.0"
    tags = ["能力工具", "搜索"]
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "搜索关键词，尽量精确"
            },
            "max_results": {
                "type": "integer",
                "description": "返回结果数量，默认5",
                "default": 5
            }
        },
        "required": ["query"]
    }

    async def execute(self, query: str, max_results: int = 5, **kwargs) -> SkillResult:
        """执行网络搜索"""
        try:
            from duckduckgo_search import DDGS

            # 使用 asyncio.to_thread 将同步调用转为异步
            results = await asyncio.to_thread(
                lambda: list(DDGS().text(query, max_results=max_results))
            )

            # 简化结果
            simplified = [
                {
                    "title": r.get("title"),
                    "snippet": r.get("body"),
                    "url": r.get("href")
                }
                for r in results
            ]

            return SkillResult(
                success=True,
                data={"query": query, "results": simplified},
                metadata={"result_count": len(simplified)}
            )
        except Exception as e:
            return SkillResult(
                success=False,
                data=None,
                error=f"搜索失败: {str(e)}"
            )
