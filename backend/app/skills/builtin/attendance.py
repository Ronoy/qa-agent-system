"""
学生考勤记录查询技能
"""
from app.skills.base import Skill, SkillResult
from app.mock.data import get_attendance_data


class AttendanceSkill(Skill):
    """查询学生考勤记录"""

    name = "get_attendance_records"
    description = "查询学生的考勤记录，包括出勤、缺勤、迟到情况"
    version = "1.0.0"
    tags = ["学情数据", "考勤"]
    parameters = {
        "type": "object",
        "properties": {
            "days": {
                "type": "integer",
                "description": "查询最近几天的记录，默认30天",
                "default": 30
            }
        },
        "required": []
    }

    async def execute(self, days: int = 30, **kwargs) -> SkillResult:
        """执行考勤查询"""
        try:
            data = get_attendance_data()
            return SkillResult(
                success=True,
                data=data,
                metadata={"days": days}
            )
        except Exception as e:
            return SkillResult(
                success=False,
                data=None,
                error=str(e)
            )
