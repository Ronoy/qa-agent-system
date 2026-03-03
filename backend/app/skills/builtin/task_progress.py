"""
任务进度查询技能
"""
from app.skills.base import Skill, SkillResult
from app.mock.data import get_task_data


class TaskProgressSkill(Skill):
    """查询学生的作业和任务完成进度"""

    name = "get_task_progress"
    description = "查询学生的作业和任务完成进度"
    version = "1.0.0"
    tags = ["学情数据", "作业"]
    parameters = {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "enum": ["all", "in_progress", "overdue", "completed", "not_started"],
                "description": "按状态筛选任务，默认返回全部",
                "default": "all"
            }
        },
        "required": []
    }

    async def execute(self, status: str = "all", **kwargs) -> SkillResult:
        """执行任务进度查询"""
        try:
            data = get_task_data()

            # 按状态筛选
            if status != "all":
                data["tasks"] = [
                    t for t in data["tasks"]
                    if t["status"] == status
                ]

            return SkillResult(
                success=True,
                data=data,
                metadata={"status_filter": status}
            )
        except Exception as e:
            return SkillResult(
                success=False,
                data=None,
                error=str(e)
            )
