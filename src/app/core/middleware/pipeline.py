"""Agent pipeline that composes middlewares into a chain.

The pipeline builds a nested call-chain from an ordered list of
middlewares and a core invoke function, similar to how ASGI/Express
middleware stacks work.
"""

from functools import reduce
from typing import Sequence

from src.app.core.middleware.types import AgentContext, AgentMiddleware, InvokeResult, NextFn


class AgentPipeline:
    """Composable middleware pipeline for agent invocations.

    Usage::

        pipeline = AgentPipeline(
            middlewares=[logging_mw, error_mw, memory_mw],
            invoke_fn=agent.core_invoke,
        )
        result = await pipeline.run(ctx)
    """

    def __init__(
        self,
        middlewares: Sequence[AgentMiddleware],
        invoke_fn: NextFn,
    ) -> None:
        self._middlewares = list(middlewares)
        self._invoke_fn = invoke_fn

    async def run(self, ctx: AgentContext) -> InvokeResult:
        """Execute the full middleware chain then the core invoke function."""
        chain = self._build_chain()
        return await chain(ctx)

    def _build_chain(self) -> NextFn:
        """Fold middlewares right-to-left so the first middleware wraps the outermost layer."""

        def wrap(next_fn: NextFn, middleware: AgentMiddleware) -> NextFn:
            async def wrapped(ctx: AgentContext) -> InvokeResult:
                return await middleware(ctx, next_fn)
            return wrapped

        return reduce(wrap, reversed(self._middlewares), self._invoke_fn)
