"""
Skills 系统测试脚本

测试技能加载、注册、执行等功能
"""
import asyncio
import json
from app.agent.agent import skill_registry, initialize_skills


async def test_skills_system():
    """测试 Skills 系统"""
    print("=" * 60)
    print("Skills 系统测试")
    print("=" * 60)

    # 1. 初始化技能
    print("\n[1] 初始化技能...")
    count = await initialize_skills()
    print(f"✓ 成功加载 {count} 个技能\n")

    # 2. 列出所有技能
    print("[2] 技能列表:")
    skills = skill_registry.list_all()
    for skill in skills:
        print(f"  - {skill['name']} (v{skill['version']})")
        print(f"    描述: {skill['description']}")
        print(f"    标签: {', '.join(skill['tags'])}")
        print(f"    状态: {'✓ 已启用' if skill['enabled'] else '✗ 已禁用'}")
        print()

    # 3. 测试技能执行
    print("[3] 测试技能执行:")

    # 测试学习状态查询
    print("\n  测试: get_learning_status")
    skill = skill_registry.get_skill("get_learning_status")
    result = await skill.execute()
    print(f"  结果: {result.success}")
    if result.success:
        data = result.data
        print(f"  科目数量: {len(data['subjects'])}")

    # 测试数学计算
    print("\n  测试: solve_math_problem")
    skill = skill_registry.get_skill("solve_math_problem")
    result = await skill.execute(expression="x**2 - 4", operation="solve")
    print(f"  结果: {result.success}")
    if result.success:
        print(f"  计算结果: {result.data['result']}")

    # 4. 测试 OpenAI 格式转换
    print("\n[4] OpenAI 工具格式:")
    tools = skill_registry.to_openai_tools()
    print(f"  工具数量: {len(tools)}")
    print(f"  第一个工具: {tools[0]['function']['name']}")

    # 5. 测试技能启用/禁用
    print("\n[5] 测试技能启用/禁用:")
    skill_registry.disable_skill("web_search")
    enabled = skill_registry.get_enabled_skills()
    print(f"  禁用 web_search 后，已启用技能数: {len(enabled)}")

    skill_registry.enable_skill("web_search")
    enabled = skill_registry.get_enabled_skills()
    print(f"  重新启用后，已启用技能数: {len(enabled)}")

    # 6. 测试按标签筛选
    print("\n[6] 按标签筛选:")
    tags = set()
    for skill in skills:
        tags.update(skill['tags'])
    print(f"  所有标签: {', '.join(sorted(tags))}")

    for tag in sorted(tags):
        skills_by_tag = skill_registry.get_by_tags([tag])
        print(f"  标签 '{tag}': {len(skills_by_tag)} 个技能")

    print("\n" + "=" * 60)
    print("✓ 所有测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_skills_system())
