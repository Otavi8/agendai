"""Middleware that adds structured logging around agent invocations."""

from src.app.core.middleware.types import AgentContext, InvokeResult, NextFn
from src.app.core.common.logging import logger


async def logging_middleware(ctx: AgentContext, next_fn: NextFn) -> InvokeResult:
    """Log invoke start and completion with session context."""
    logger.info(
        "agent_invoke_started",
        agent_name=ctx.agent_name,
        session_id=ctx.session_id,
        user_id=ctx.user_id,
        message_count=len(ctx.messages),
    )

    result = await next_fn(ctx)

    logger.info(
        "agent_invoke_completed",
        agent_name=ctx.agent_name,
        session_id=ctx.session_id,
        result_count=len(result),
    )
    return result
