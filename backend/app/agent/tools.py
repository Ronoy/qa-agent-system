import json
import asyncio
from app.mock.data import get_attendance_data, get_learning_data, get_task_data, get_knowledge_data

# ── 工具定义（OpenAI function calling 格式）──────────────────────────────────

TOOLS = [
    # ── 原有 5 个工具 ──
    {
        "type": "function",
        "function": {
            "name": "get_attendance_records",
            "description": "查询学生的考勤记录，包括出勤、缺勤、迟到情况",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "查询最近几天的记录，默认30天", "default": 30}
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
                    "subject": {"type": "string", "description": "指定科目，如'数学'、'英语'等，不填则返回所有科目"}
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
                    "subject": {"type": "string", "description": "指定科目，不填则返回所有科目的知识点"},
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
                    "focus": {"type": "string", "description": "重点关注方向，如'薄弱科目'、'紧急任务'等"}
                },
                "required": []
            }
        }
    },

    # ── 新增工具 ──
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "联网搜索最新信息，适用于查询时事、政策、考试资讯、学科前沿知识等实时内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词，尽量精确"},
                    "max_results": {"type": "integer", "description": "返回结果数量，默认5", "default": 5}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "solve_math_problem",
            "description": "数学计算工具，支持方程求解、求导、积分、化简、因式分解等精确计算",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，使用 Python/sympy 语法，如 'x**2 - 4'、'sin(x)'、'x**2 + 2*x + 1'"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["solve", "diff", "integrate", "simplify", "factor", "expand", "limit"],
                        "description": "操作类型：solve=求解方程, diff=求导, integrate=积分, simplify=化简, factor=因式分解, expand=展开, limit=求极限"
                    },
                    "variable": {
                        "type": "string",
                        "description": "变量名，默认为 x",
                        "default": "x"
                    },
                    "extra": {
                        "type": "string",
                        "description": "附加参数，如 limit 操作时的趋近值 '0' 或 'oo'（无穷大）"
                    }
                },
                "required": ["expression", "operation"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_practice_problems",
            "description": "根据学生薄弱知识点自动生成针对性练习题，帮助巩固薄弱环节",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string", "description": "科目，如'数学'、'物理'、'英语'"},
                    "topic": {"type": "string", "description": "具体知识点或题型，如'二次函数'、'牛顿第二定律'"},
                    "difficulty": {
                        "type": "string",
                        "enum": ["easy", "medium", "hard"],
                        "description": "难度：easy=基础, medium=中等, hard=拔高",
                        "default": "medium"
                    },
                    "count": {"type": "integer", "description": "生成题目数量，默认3道", "default": 3}
                },
                "required": ["subject", "topic"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_study_plan",
            "description": "结合学生当前学情、薄弱知识点和待完成任务，生成个性化学习计划",
            "parameters": {
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
        }
    },
    {
        "type": "function",
        "function": {
            "name": "explain_concept",
            "description": "深度讲解某个学科知识点，包括定义、原理、公式、例题和常见错误",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string", "description": "科目"},
                    "concept": {"type": "string", "description": "要讲解的知识点，如'导数的定义'、'光合作用'、'文言文虚词'"},
                    "depth": {
                        "type": "string",
                        "enum": ["brief", "detailed"],
                        "description": "讲解深度：brief=简要概述, detailed=深度讲解含例题",
                        "default": "detailed"
                    }
                },
                "required": ["subject", "concept"]
            }
        }
    }
]

# ── 工具执行 ─────────────────────────────────────────────────────────────────

async def execute_tool(tool_name: str, tool_args: dict) -> str:
    """执行工具调用并返回结果字符串（async）"""

    # ── 原有工具 ──
    if tool_name == "get_attendance_records":
        return json.dumps(get_attendance_data(), ensure_ascii=False)

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

    # ── 联网搜索 ──
    elif tool_name == "web_search":
        return await _web_search(tool_args)

    # ── 数学求解 ──
    elif tool_name == "solve_math_problem":
        return _solve_math(tool_args)

    # ── 生成练习题（返回上下文，由 LLM 生成题目） ──
    elif tool_name == "generate_practice_problems":
        knowledge = get_knowledge_data()
        learning = get_learning_data()
        subject = tool_args.get("subject", "")
        topic = tool_args.get("topic", "")
        weak = [kp for kp in knowledge["knowledge_points"]
                if kp["subject"] == subject and kp["level"] in ("weak", "medium")]
        subj_data = next((s for s in learning["subjects"] if s["subject"] == subject), {})
        return json.dumps({
            "instruction": "请根据以下信息生成练习题",
            "subject": subject,
            "topic": topic,
            "difficulty": tool_args.get("difficulty", "medium"),
            "count": tool_args.get("count", 3),
            "student_weak_points": weak[:5],
            "current_score": subj_data.get("score"),
        }, ensure_ascii=False)

    # ── 制定学习计划（返回学情数据，由 LLM 生成计划） ──
    elif tool_name == "create_study_plan":
        learning = get_learning_data()
        tasks = get_task_data()
        knowledge = get_knowledge_data()
        pending = [t for t in tasks["tasks"] if t["status"] in ("not_started", "in_progress", "overdue")]
        weak_subjects = sorted(learning["subjects"], key=lambda s: s["score"])[:3]
        return json.dumps({
            "instruction": "请根据以下学情数据制定学习计划",
            "duration_days": tool_args.get("duration_days", 7),
            "daily_hours": tool_args.get("daily_hours", 3),
            "focus_subjects": tool_args.get("focus_subjects") or [s["subject"] for s in weak_subjects],
            "weak_subjects": weak_subjects,
            "pending_tasks": pending[:5],
            "weak_knowledge_points": knowledge["weak_points"][:6],
        }, ensure_ascii=False)

    # ── 讲解知识点（返回结构化请求，由 LLM 讲解） ──
    elif tool_name == "explain_concept":
        knowledge = get_knowledge_data()
        subject = tool_args.get("subject", "")
        concept = tool_args.get("concept", "")
        related = [kp for kp in knowledge["knowledge_points"]
                   if kp["subject"] == subject][:3]
        return json.dumps({
            "instruction": "请深度讲解以下知识点",
            "subject": subject,
            "concept": concept,
            "depth": tool_args.get("depth", "detailed"),
            "related_weak_points": related,
        }, ensure_ascii=False)

    return json.dumps({"error": f"未知工具: {tool_name}"}, ensure_ascii=False)


# ── 内部实现 ──────────────────────────────────────────────────────────────────

async def _web_search(args: dict) -> str:
    query = args.get("query", "")
    max_results = args.get("max_results", 5)
    try:
        from duckduckgo_search import DDGS
        results = await asyncio.to_thread(
            lambda: list(DDGS().text(query, max_results=max_results))
        )
        simplified = [{"title": r.get("title"), "snippet": r.get("body"), "url": r.get("href")}
                      for r in results]
        return json.dumps({"query": query, "results": simplified}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"搜索失败: {str(e)}", "query": query}, ensure_ascii=False)


def _solve_math(args: dict) -> str:
    try:
        from sympy import symbols, sympify, solve, diff, integrate, simplify, factor, expand, limit, oo, latex
        from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

        var_name = args.get("variable", "x")
        operation = args.get("operation", "simplify")
        expr_str = args.get("expression", "")
        extra = args.get("extra", "")

        x = symbols(var_name)
        transformations = standard_transformations + (implicit_multiplication_application,)
        expr = parse_expr(expr_str, local_dict={var_name: x}, transformations=transformations)

        if operation == "solve":
            result = solve(expr, x)
            result_str = str(result)
            result_latex = [latex(r) for r in result]
        elif operation == "diff":
            result = diff(expr, x)
            result_str = str(result)
            result_latex = [latex(result)]
        elif operation == "integrate":
            result = integrate(expr, x)
            result_str = str(result)
            result_latex = [latex(result)]
        elif operation == "simplify":
            result = simplify(expr)
            result_str = str(result)
            result_latex = [latex(result)]
        elif operation == "factor":
            result = factor(expr)
            result_str = str(result)
            result_latex = [latex(result)]
        elif operation == "expand":
            result = expand(expr)
            result_str = str(result)
            result_latex = [latex(result)]
        elif operation == "limit":
            point = oo if extra in ("oo", "inf", "∞") else sympify(extra or "0")
            result = limit(expr, x, point)
            result_str = str(result)
            result_latex = [latex(result)]
        else:
            return json.dumps({"error": f"不支持的操作: {operation}"}, ensure_ascii=False)

        return json.dumps({
            "expression": expr_str,
            "operation": operation,
            "variable": var_name,
            "result": result_str,
            "result_latex": result_latex,
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"计算失败: {str(e)}", "expression": args.get("expression")},
                          ensure_ascii=False)
