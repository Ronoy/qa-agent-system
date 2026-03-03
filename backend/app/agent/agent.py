"""
智能体主循环 - 使用 Skills 系统

支持动态工具加载和执行
"""
import json
from typing import AsyncGenerator
from openai import AsyncOpenAI
from app.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from app.skills import SkillRegistry, SkillLoader
from app.agent.prompts import build_dynamic_prompt

# 初始化 OpenAI 客户端
client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

# 全局技能注册中心
skill_registry = SkillRegistry()


async def initialize_skills():
    """初始化并加载所有内置技能"""
    count = await SkillLoader.load_from_directory("app/skills/builtin", skill_registry)
    print(f"\n{'='*50}")
    print(f"✓ Skills 系统初始化完成，已加载 {count} 个技能")
    print(f"{'='*50}\n")
    return count


async def run_agent_stream(
    user_message: str,
    history: list[dict],
    attachments: list[dict] = None,
    kb_ids: list[dict] = None,
    model: str = None,
) -> AsyncGenerator[dict, None]:
    """
    Agent 主循环：工具调用（非流式）→ 注入结果 → 流式输出最终回答
    """
    enabled_skills = skill_registry.get_enabled_skills()
    system_prompt = build_dynamic_prompt(enabled_skills)
    active_model = model or DEEPSEEK_MODEL

    if kb_ids:
        kb_list = "\n".join(f"- {kb['name']}（ID: {kb['id']}）" for kb in kb_ids)
        system_prompt += f"\n\n## 可用知识库\n用户已关联以下知识库，回答问题时应优先调用 search_knowledge_base 工具检索相关内容：\n{kb_list}"

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)

    # 构建用户消息（支持多模态）
    if attachments:
        content = []
        has_image = False

        for att in attachments:
            if att["file_type"] == "image" and att["extracted_text"].startswith("[IMAGE_BASE64:"):
                # 提取 base64 数据
                b64 = att["extracted_text"][len("[IMAGE_BASE64:"):-1]
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                })
                has_image = True
            elif att["file_type"] == "pdf":
                user_message += f"\n\n[附件: {att['file_name']}]\n{att['extracted_text']}"

        if has_image:
            content.insert(0, {"type": "text", "text": user_message})
            messages.append({"role": "user", "content": content})
        else:
            messages.append({"role": "user", "content": user_message})
    else:
        messages.append({"role": "user", "content": user_message})

    # 工具调用循环（最多 5 轮防止死循环）
    for iteration in range(5):
        response = await client.chat.completions.create(
            model=active_model,
            messages=messages,
            tools=skill_registry.to_openai_tools(),
            tool_choice="auto",
            stream=False,
        )
        msg = response.choices[0].message

        # 没有工具调用 → 退出循环，进入流式输出
        if not msg.tool_calls:
            break

        # 有工具调用 → 执行并注入结果
        messages.append(msg.model_dump(exclude_none=True))

        for tc in msg.tool_calls:
            tool_name = tc.function.name
            try:
                tool_args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                tool_args = {}

            yield {"type": "tool_call", "tool_name": tool_name, "tool_args": tool_args}

            # 从注册中心获取技能并执行
            skill = skill_registry.get_skill(tool_name)
            if skill:
                try:
                    result = await skill.execute(**tool_args)
                    result_content = result.to_json()
                except Exception as e:
                    result_content = json.dumps({
                        "success": False,
                        "error": f"技能执行失败: {str(e)}"
                    }, ensure_ascii=False)
            else:
                result_content = json.dumps({
                    "success": False,
                    "error": f"未找到技能: {tool_name}"
                }, ensure_ascii=False)

            yield {"type": "tool_result", "tool_name": tool_name, "content": result_content}

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result_content,
            })

    # 流式输出最终回答
    stream = await client.chat.completions.create(
        model=active_model,
        messages=messages,
        stream=True,
    )

    async for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield {"type": "text", "content": delta.content}

    yield {"type": "done"}
