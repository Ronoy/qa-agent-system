"""
知识点讲解技能
"""
from app.skills.base import Skill, SkillResult
from app.mock.data import get_knowledge_data


class ConceptExplainSkill(Skill):
    """深度讲解某个学科知识点"""

    name = "explain_concept"
    description = "深度讲解某个学科知识点，包括定义、原理、公式、例题和常见错误"
    version = "1.0.0"
    tags = ["能力工具", "讲解"]
    parameters = {
        "type": "object",
        "properties": {
            "subject": {
                "type": "string",
                "description": "科目"
            },
            "concept": {
                "type": "string",
                "description": "要讲解的知识点，如'导数的定义'、'光合作用'、'文言文虚词'"
            },
            "depth": {
                "type": "string",
                "enum": ["brief", "detailed"],
                "description": "讲解深度：brief=简要概述, detailed=深度讲解含例题",
                "default": "detailed"
            }
        },
        "required": ["subject", "concept"]
    }

    async def execute(self, subject: str, concept: str, depth: str = "detailed", **kwargs) -> SkillResult:
        """讲解知识点（返回结构化请求，由 LLM 讲解）"""
        try:
            knowledge = get_knowledge_data()

            # 查找相关知识点
            related = [
                kp for kp in knowledge["knowledge_points"]
                if kp["subject"] == subject
            ][:3]

            return SkillResult(
                success=True,
                data={
                    "instruction": "请深度讲解以下知识点",
                    "subject": subject,
                    "concept": concept,
                    "depth": depth,
                    "related_weak_points": related
                }
            )
        except Exception as e:
            return SkillResult(
                success=False,
                data=None,
                error=str(e)
            )
