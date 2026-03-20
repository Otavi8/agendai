"""Core types for the agent middleware pattern.

Defines the context object passed through the middleware chain,
the result type, and the middleware protocol that all middlewares implement.
"""

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Optional, Protocol, runtime_checkable

from src.app.core.common.config import settings
from src.app.core.common.model.message import Message
from src.app.init import langfuse_callback_handler

InvokeResult = list[Message]

NextFn = Callable[["AgentContext"], Awaitable[InvokeResult]]


@dataclass
class AgentContext:
    """Shared context threaded through the middleware chain.

    Middlewares can read/write ``metadata`` to pass data downstream
    (e.g. ``long_term_memory`` populated by the memory middleware).
    """

    messages: list[Message]
    session_id: str
    user_id: Optional[int]
    config: dict
    agent_name: str
    metadata: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class AgentMiddleware(Protocol):
    """Protocol every middleware must satisfy.

    A middleware receives the current context and a ``next_fn`` that
    invokes the remainder of the chain.  It may short-circuit by
    returning early or modify the context/result around the call.
    """

    async def __call__(self, ctx: AgentContext, next_fn: NextFn) -> InvokeResult: ...


def build_invoke_config(
    session_id: str,
    user_id: Optional[int] = None,
    agent_name: str = "",
) -> dict:
    """Build a LangGraph invoke config shared across all agents.

    Centralises the duplicated ``_build_invoke_config`` /
    ``get_config`` helpers that existed in each agent class.
    """
    return {
        "callbacks": [langfuse_callback_handler],
        "run_name": agent_name,
        "configurable": {"thread_id": session_id},
        "metadata": {
            "environment": settings.ENVIRONMENT.value,
            "debug": settings.DEBUG,
            "user_id": user_id,
            "session_id": session_id,
        },
    }
