"""Middleware that integrates long-term memory retrieval and update."""

from src.app.agents.middleware.types import AgentContext, InvokeResult, NextFn
from src.app.core.memory.memory import bg_update_memory, get_relevant_memory


async def memory_middleware(ctx: AgentContext, next_fn: NextFn) -> InvokeResult:
    """Retrieve relevant memory before invoke, update memory after."""
    if ctx.messages:
        memory = await get_relevant_memory(ctx.user_id, ctx.messages[-1].content)
        ctx.metadata["long_term_memory"] = memory or "No relevant memory found."

    result = await next_fn(ctx)

    if result:
        messages_dict = [dict(role=m.role, content=str(m.content)) for m in result]
        bg_update_memory(
            ctx.user_id,
            messages_dict,
            {
                "session_id": ctx.session_id,
                "agent_name": ctx.agent_name,
                "user_id": ctx.user_id,
            },
        )

    return result
