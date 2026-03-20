"""Composable middleware for agent invocations.

Usage::

    from src.app.core.middleware import (
        AgentContext,
        AgentPipeline,
        error_handling_middleware,
        logging_middleware,
        memory_middleware,
        create_guardrail_middleware,
    )

    pipeline = AgentPipeline(
        middlewares=[logging_middleware, error_handling_middleware, memory_middleware],
        invoke_fn=agent.core_invoke,
    )
    result = await pipeline.run(ctx)
"""

from src.app.core.middleware.error_handling_middleware import error_handling_middleware
from src.app.core.middleware.guardrail_middleware import create_guardrail_middleware
from src.app.core.middleware.logging_middleware import logging_middleware
from src.app.core.middleware.memory_middleware import memory_middleware
from src.app.core.middleware.pipeline import AgentPipeline
from src.app.core.middleware.types import AgentContext, AgentMiddleware, InvokeResult, NextFn, build_invoke_config
