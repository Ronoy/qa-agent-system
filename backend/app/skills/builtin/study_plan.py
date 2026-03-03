"""
学习计划制定技能
"""
from app.skills.base import Skill, SkillResult
from app.mock.data import get_learning_data, get_task_data, get_knowledge_data


class StudyPlanSkill(Skill):
    """结合学生当前学情、薄弱知识点和待完成任务，生成个性化学习计划"""

    name = "create_study_plan"
    description = "结合学生当前学情、薄弱知识点和待完成任务，生成个性化学习计划"
    version = "1.0.0"
    tags = ["能力工具", "计划"]
    parameters = {
        "type": "object",
        "properties": {
            "duration_days": {
                "type": "integer",
                "description": "计划周期（天），如7=一周计划，30=月计划",
                "default": 7
            },
            "focus_subjects": {
                "type": "array",
                "items": {"type": "string"},
                "description": "重点提升的科目列表，不填则根据学情自动选择"
            },
            "daily_hours": {
                "type": "number",
                "description": "每天可用学习时长（小时），默认3小时",
                "default": 3
            }
        },
        "required": []
    }

    async def execute(self, duration_days: int = 7, focus_subjects: list = None, daily_hours: float = 3, **kwargs) -> SkillResult:
        """制定学习计划（返回学情数据，由 LLM 生成计划）"""
        try:
            learning = get_learning_data()
            tasks = get_task_data()
            knowledge = get_knowledge_data()

            # 待完成任务
            pending = [
                t for t in tasks["tasks"]
                if t["status"] in ("not_started", "in_progress", "overdue")
            ]

            # 薄弱科目（按成绩排序）
            weak_subjects = sorted(learning["subjects"], key=lambda s: s["score"])[:3]

            return SkillResult(
                success=True,
                data={
                    "instruction": "请根据以下学情数据制定学习计划",
                    "duration_days": duration_days,
                    "daily_hours": daily_hours,
                    "focus_subjects": focus_subjects or [s["subject"] for s in weak_subjects],
                    "weak_subjects": weak_subjects,
                    "pending_tasks": pending[:5],
                    "weak_knowledge_points": knowledge["weak_points"][:6]
                }
            )
        except Exception as e:
            return SkillResult(
                success=False,
                data=None,
                error=str(e)
            )
