from datetime import date, timedelta
import random

STUDENT_ID = "stu_001"
STUDENT_NAME = "张同学"

# 考勤模拟数据
def get_attendance_data():
    records = []
    today = date.today()
    for i in range(30):
        d = today - timedelta(days=i)
        if d.weekday() < 5:  # 工作日
            status = random.choices(
                ["present", "absent", "late"],
                weights=[85, 5, 10]
            )[0]
            records.append({
                "date": d.isoformat(),
                "status": status,
                "course": random.choice(["数学", "语文", "英语", "物理", "化学"]),
                "remark": "迟到5分钟" if status == "late" else ""
            })
    return {
        "student_id": STUDENT_ID,
        "student_name": STUDENT_NAME,
        "total_days": len(records),
        "present": sum(1 for r in records if r["status"] == "present"),
        "absent": sum(1 for r in records if r["status"] == "absent"),
        "late": sum(1 for r in records if r["status"] == "late"),
        "records": records[:10]  # 返回最近10条
    }


# 学情模拟数据
def get_learning_data():
    subjects = [
        {"subject": "数学", "score": 78, "progress": 65, "rank": 12, "trend": "up"},
        {"subject": "语文", "score": 85, "progress": 80, "rank": 8, "trend": "stable"},
        {"subject": "英语", "score": 62, "progress": 55, "rank": 25, "trend": "down"},
        {"subject": "物理", "score": 90, "progress": 88, "rank": 3, "trend": "up"},
        {"subject": "化学", "score": 71, "progress": 70, "rank": 18, "trend": "stable"},
    ]
    return {
        "student_id": STUDENT_ID,
        "student_name": STUDENT_NAME,
        "overall_score": round(sum(s["score"] for s in subjects) / len(subjects), 1),
        "overall_rank": 15,
        "class_size": 40,
        "subjects": subjects
    }


# 任务模拟数据
def get_task_data():
    tasks = [
        {"id": "t1", "title": "数学第三章练习册", "subject": "数学", "due_date": "2026-03-05", "status": "in_progress", "progress": 60},
        {"id": "t2", "title": "英语阅读理解专项", "subject": "英语", "due_date": "2026-03-03", "status": "overdue", "progress": 30},
        {"id": "t3", "title": "物理实验报告", "subject": "物理", "due_date": "2026-03-10", "status": "not_started", "progress": 0},
        {"id": "t4", "title": "语文作文修改", "subject": "语文", "due_date": "2026-02-28", "status": "completed", "progress": 100},
        {"id": "t5", "title": "化学方程式背诵", "subject": "化学", "due_date": "2026-03-07", "status": "in_progress", "progress": 45},
    ]
    return {
        "student_id": STUDENT_ID,
        "student_name": STUDENT_NAME,
        "total": len(tasks),
        "completed": sum(1 for t in tasks if t["status"] == "completed"),
        "in_progress": sum(1 for t in tasks if t["status"] == "in_progress"),
        "overdue": sum(1 for t in tasks if t["status"] == "overdue"),
        "not_started": sum(1 for t in tasks if t["status"] == "not_started"),
        "tasks": tasks
    }


# 知识点掌握度模拟数据
def get_knowledge_data():
    knowledge_points = [
        {"subject": "数学", "topic": "二次函数", "mastery": 85, "level": "good"},
        {"subject": "数学", "topic": "三角函数", "mastery": 55, "level": "weak"},
        {"subject": "数学", "topic": "数列", "mastery": 70, "level": "medium"},
        {"subject": "英语", "topic": "时态语法", "mastery": 60, "level": "medium"},
        {"subject": "英语", "topic": "词汇量", "mastery": 45, "level": "weak"},
        {"subject": "物理", "topic": "力学", "mastery": 92, "level": "excellent"},
        {"subject": "物理", "topic": "电磁学", "mastery": 78, "level": "good"},
        {"subject": "化学", "topic": "有机化学", "mastery": 65, "level": "medium"},
        {"subject": "化学", "topic": "化学方程式", "mastery": 50, "level": "weak"},
    ]
    weak_points = [kp for kp in knowledge_points if kp["level"] in ("weak",)]
    return {
        "student_id": STUDENT_ID,
        "student_name": STUDENT_NAME,
        "knowledge_points": knowledge_points,
        "weak_count": len(weak_points),
        "weak_points": weak_points
    }
