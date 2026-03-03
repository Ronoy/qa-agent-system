"""
数学问题求解技能
"""
from app.skills.base import Skill, SkillResult


class MathSolverSkill(Skill):
    """数学计算工具，支持方程求解、求导、积分等"""

    name = "solve_math_problem"
    description = "数学计算工具，支持方程求解、求导、积分、化简、因式分解等精确计算"
    version = "1.0.0"
    tags = ["能力工具", "数学"]
    parameters = {
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

    async def execute(self, expression: str, operation: str, variable: str = "x", extra: str = "", **kwargs) -> SkillResult:
        """执行数学计算"""
        try:
            from sympy import symbols, solve, diff, integrate, simplify, factor, expand, limit, oo, latex
            from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

            # 创建符号变量
            x = symbols(variable)
            transformations = standard_transformations + (implicit_multiplication_application,)
            expr = parse_expr(expression, local_dict={variable: x}, transformations=transformations)

            # 执行操作
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
                from sympy import sympify
                point = oo if extra in ("oo", "inf", "∞") else sympify(extra or "0")
                result = limit(expr, x, point)
                result_str = str(result)
                result_latex = [latex(result)]
            else:
                return SkillResult(
                    success=False,
                    data=None,
                    error=f"不支持的操作: {operation}"
                )

            return SkillResult(
                success=True,
                data={
                    "expression": expression,
                    "operation": operation,
                    "variable": variable,
                    "result": result_str,
                    "result_latex": result_latex
                }
            )
        except Exception as e:
            return SkillResult(
                success=False,
                data=None,
                error=f"计算失败: {str(e)}"
            )
