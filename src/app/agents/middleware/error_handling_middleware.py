"""Middleware that provides consistent error handling across agents."""

from src.app.agents.middleware.types import AgentContext, InvokeResult, NextFn
from src.app.core.common.config import Environment, settings
from src.app.core.common.logging import logger
from src.app.core.llm.llm_utils import record_llm_error


async def error_handling_middleware(ctx: AgentContext, next_fn: NextFn) -> InvokeResult:
    """Catch exceptions, record metrics, re-raise in dev, return fallback otherwise."""
    try:
        return await next_fn(ctx)
    except Exception as e:
        model_name = ctx.metadata.get("model_name", "unknown")
        record_llm_error(model_name, ctx.agent_name)

        if settings.ENVIRONMENT == Environment.DEVELOPMENT:
            raise

        logger.exception(
            "agent_invoke_failed",
            agent_name=ctx.agent_name,
            session_id=ctx.session_id,
            error=str(e),
        )
        return []
