"""
学生学习状态查询技能
"""
from app.skills.base import Skill, SkillResult
from app.mock.data import get_learning_data


class LearningStatusSkill(Skill):
    """查询学生各科目的学习情况"""

    name = "get_learning_status"
    description = "查询学生各科目的学习情况，包括成绩、进度、班级排名和趋势"
    version = "1.0.0"
    tags = ["学情数据", "成绩"]
    parameters = {
        "type": "object",
        "properties": {
            "subject": {
                "type": "string",
                "description": "指定科目，如'数学'、'英语'等，不填则返回所有科目"
            }
        },
        "required": []
    }

    async def execute(self, subject: str = None, **kwargs) -> SkillResult:
        """执行学习状态查询"""
        try:
            data = get_learning_data()

            # 如果指定了科目，进行筛选
            if subject:
                data["subjects"] = [
                    s for s in data["subjects"]
                    if s["subject"] == subject
                ]

            return SkillResult(
                success=True,
                data=data,
                metadata={"subject": subject}
            )
        except Exception as e:
            return SkillResult(
                success=False,
                data=None,
                error=str(e)
            )
