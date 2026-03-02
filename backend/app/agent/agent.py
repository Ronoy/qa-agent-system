import json
from typing import AsyncGenerator
from openai import AsyncOpenAI
from app.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from app.agent.tools import TOOLS, execute_tool
from app.agent.prompts import SYSTEM_PROMPT

client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)


async def run_agent_stream(
    user_message: str,
    history: list[dict]
) -> AsyncGenerator[dict, None]:
    """
    Agent 主循环：工具调用（非流式）→ 注入结果 → 流式输出最终回答
    每次 yield 一个事件 dict: {type, content?, tool_name?, tool_args?}
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    # 工具调用循环（最多 5 轮防止死循环）
    for _ in range(5):
        response = await client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=messages,
            tools=TOOLS,
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

            result = await execute_tool(tool_name, tool_args)

            yield {"type": "tool_result", "tool_name": tool_name, "content": result}

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    # 流式输出最终回答
    stream = await client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=messages,
        stream=True,
    )

    async for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield {"type": "text", "content": delta.content}

    yield {"type": "done"}
