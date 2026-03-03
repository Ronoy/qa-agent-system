"""
练习题生成技能
"""
from app.skills.base import Skill, SkillResult
from app.mock.data import get_knowledge_data, get_learning_data


class PracticeProblemsSkill(Skill):
    """根据学生薄弱知识点自动生成针对性练习题"""

    name = "generate_practice_problems"
    description = "根据学生薄弱知识点自动生成针对性练习题，帮助巩固薄弱环节"
    version = "1.0.0"
    tags = ["能力工具", "题目生成"]
    parameters = {
        "type": "object",
        "properties": {
            "subject": {
                "type": "string",
                "description": "科目，如'数学'、'物理'、'英语'"
            },
            "topic": {
                "type": "string",
                "description": "具体知识点或题型，如'二次函数'、'牛顿第二定律'"
            },
            "difficulty": {
                "type": "string",
                "enum": ["easy", "medium", "hard"],
                "description": "难度：easy=基础, medium=中等, hard=拔高",
                "default": "medium"
            },
            "count": {
                "type": "integer",
                "description": "生成题目数量，默认3道",
                "default": 3
            }
        },
        "required": ["subject", "topic"]
    }

    async def execute(self, subject: str, topic: str, difficulty: str = "medium", count: int = 3, **kwargs) -> SkillResult:
        """生成练习题（返回上下文，由 LLM 生成题目）"""
        try:
            knowledge = get_knowledge_data()
            learning = get_learning_data()

            # 查找相关薄弱知识点
            weak = [
                kp for kp in knowledge["knowledge_points"]
                if kp["subject"] == subject and kp["level"] in ("weak", "medium")
            ]

            # 获取科目成绩
            subj_data = next((s for s in learning["subjects"] if s["subject"] == subject), {})

            return SkillResult(
                success=True,
                data={
                    "instruction": "请根据以下信息生成练习题",
                    "subject": subject,
                    "topic": topic,
                    "difficulty": difficulty,
                    "count": count,
                    "student_weak_points": weak[:5],
                    "current_score": subj_data.get("score")
                }
            )
        except Exception as e:
            return SkillResult(
                success=False,
                data=None,
                error=str(e)
            )
