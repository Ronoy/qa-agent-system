from app.mock.data import get_attendance_data, get_learning_data, get_task_data, get_knowledge_data
import json

# 工具定义（OpenAI function calling 格式）
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_attendance_records",
            "description": "查询学生的考勤记录，包括出勤、缺勤、迟到情况",
            "parameters": {
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
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_learning_status",
            "description": "查询学生各科目的学习情况，包括成绩、进度、班级排名和趋势",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "指定科目，如'数学'、'英语'等，不填则返回所有科目"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_task_progress",
            "description": "查询学生的作业和任务完成进度",
            "parameters": {
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
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_knowledge_mastery",
            "description": "查询学生各知识点的掌握程度，识别薄弱知识点",
            "parameters": {
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
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_learning_recommendations",
            "description": "根据学生的学情、任务和知识点掌握情况，生成个性化学习建议",
            "parameters": {
                "type": "object",
                "properties": {
                    "focus": {
                        "type": "string",
                        "description": "重点关注方向，如'薄弱科目'、'紧急任务'等"
                    }
                },
                "required": []
            }
        }
    }
]


def execute_tool(tool_name: str, tool_args: dict) -> str:
    """执行工具调用并返回结果字符串"""
    if tool_name == "get_attendance_records":
        data = get_attendance_data()
        return json.dumps(data, ensure_ascii=False)

    elif tool_name == "get_learning_status":
        data = get_learning_data()
        subject = tool_args.get("subject")
        if subject:
            data["subjects"] = [s for s in data["subjects"] if s["subject"] == subject]
        return json.dumps(data, ensure_ascii=False)

    elif tool_name == "get_task_progress":
        data = get_task_data()
        status_filter = tool_args.get("status", "all")
        if status_filter != "all":
            data["tasks"] = [t for t in data["tasks"] if t["status"] == status_filter]
        return json.dumps(data, ensure_ascii=False)

    elif tool_name == "get_knowledge_mastery":
        data = get_knowledge_data()
        subject = tool_args.get("subject")
        level = tool_args.get("level", "all")
        kps = data["knowledge_points"]
        if subject:
            kps = [kp for kp in kps if kp["subject"] == subject]
        if level != "all":
            kps = [kp for kp in kps if kp["level"] == level]
        data["knowledge_points"] = kps
        return json.dumps(data, ensure_ascii=False)

    elif tool_name == "get_learning_recommendations":
        learning = get_learning_data()
        tasks = get_task_data()
        knowledge = get_knowledge_data()
        rec = {
            "weak_subjects": [s for s in learning["subjects"] if s["score"] < 70],
            "overdue_tasks": [t for t in tasks["tasks"] if t["status"] == "overdue"],
            "weak_knowledge_points": knowledge["weak_points"],
            "priority_actions": []
        }
        if rec["overdue_tasks"]:
            rec["priority_actions"].append(f"立即完成逾期任务：{rec['overdue_tasks'][0]['title']}")
        if rec["weak_subjects"]:
            rec["priority_actions"].append(f"重点提升薄弱科目：{rec['weak_subjects'][0]['subject']}")
        if rec["weak_knowledge_points"]:
            rec["priority_actions"].append(f"强化薄弱知识点：{rec['weak_knowledge_points'][0]['topic']}")
        return json.dumps(rec, ensure_ascii=False)

    return json.dumps({"error": f"未知工具: {tool_name}"}, ensure_ascii=False)
