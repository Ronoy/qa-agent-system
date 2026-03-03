"""
知识点掌握度查询技能
"""
from app.skills.base import Skill, SkillResult
from app.mock.data import get_knowledge_data


class KnowledgeMasterySkill(Skill):
    """查询学生各知识点的掌握程度"""

    name = "get_knowledge_mastery"
    description = "查询学生各知识点的掌握程度，识别薄弱知识点"
    version = "1.0.0"
    tags = ["学情数据", "知识点"]
    parameters = {
        "type": "object",
        "properties": {
            "subject": {
                "type": "string",
                "description": "指定科目，不填则返回所有科目的知识点"
            },
            "level": {
                "type": "string",
                "enum": ["all", "weak", "medium", "good", "excellent"],
                "description": "按掌握程度筛选，默认返回全部",
                "default": "all"
            }
        },
        "required": []
    }

    async def execute(self, subject: str = None, level: str = "all", **kwargs) -> SkillResult:
        """执行知识点掌握度查询"""
        try:
            data = get_knowledge_data()
            kps = data["knowledge_points"]

            # 按科目筛选
            if subject:
                kps = [kp for kp in kps if kp["subject"] == subject]

            # 按掌握程度筛选
            if level != "all":
                kps = [kp for kp in kps if kp["level"] == level]

            data["knowledge_points"] = kps

            return SkillResult(
                success=True,
                data=data,
                metadata={"subject": subject, "level": level}
            )
        except Exception as e:
            return SkillResult(
                success=False,
                data=None,
                error=str(e)
            )
