"""
学习建议生成技能
"""
from app.skills.base import Skill, SkillResult
from app.mock.data import get_learning_data, get_task_data, get_knowledge_data


class LearningRecommendationsSkill(Skill):
    """根据学生的学情、任务和知识点掌握情况，生成个性化学习建议"""

    name = "get_learning_recommendations"
    description = "根据学生的学情、任务和知识点掌握情况，生成个性化学习建议"
    version = "1.0.0"
    tags = ["学情数据", "建议"]
    parameters = {
        "type": "object",
        "properties": {
            "focus": {
                "type": "string",
                "description": "重点关注方向，如'薄弱科目'、'紧急任务'等"
            }
        },
        "required": []
    }

    async def execute(self, focus: str = None, **kwargs) -> SkillResult:
        """生成学习建议"""
        try:
            learning = get_learning_data()
            tasks = get_task_data()
            knowledge = get_knowledge_data()

            # 分析薄弱科目
            weak_subjects = [s for s in learning["subjects"] if s["score"] < 70]

            # 分析逾期任务
            overdue_tasks = [t for t in tasks["tasks"] if t["status"] == "overdue"]

            # 薄弱知识点
            weak_points = knowledge["weak_points"]

            # 生成优先行动建议
            priority_actions = []
            if overdue_tasks:
                priority_actions.append(f"立即完成逾期任务：{overdue_tasks[0]['title']}")
            if weak_subjects:
                priority_actions.append(f"重点提升薄弱科目：{weak_subjects[0]['subject']}")
            if weak_points:
                priority_actions.append(f"强化薄弱知识点：{weak_points[0]['topic']}")

            recommendations = {
                "weak_subjects": weak_subjects,
                "overdue_tasks": overdue_tasks,
                "weak_knowledge_points": weak_points,
                "priority_actions": priority_actions
            }

            return SkillResult(
                success=True,
                data=recommendations,
                metadata={"focus": focus}
            )
        except Exception as e:
            return SkillResult(
                success=False,
                data=None,
                error=str(e)
            )
