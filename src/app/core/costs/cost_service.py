"""LLM token usage, cost estimation, and budget controls."""

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Optional

from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig

from src.app.core.common.config import settings
from src.app.core.common.logging import logger
from src.app.core.costs.cost_model import LLMUsageRecord
from src.app.core.costs.cost_repository import LLMCostRepository
from src.app.core.db.database import database_factory
from src.app.core.metrics.metrics import llm_budget_exceeded_total, llm_cost_usd_total, llm_request_cost_usd


@dataclass(frozen=True)
class TokenUsage:
    """Normalized token usage extracted from a LangChain response."""

    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass(frozen=True)
class ModelPricing:
    """USD pricing per 1M tokens."""

    input_usd_per_1m: float
    output_usd_per_1m: float
    source: str


@dataclass(frozen=True)
class EstimatedCost:
    """Computed LLM cost for one response."""

    input_cost_usd: float
    output_cost_usd: float
    total_cost_usd: float
    pricing_source: str


class LLMBudgetExceededError(RuntimeError):
    """Raised when an LLM request is blocked by configured budget controls."""


DEFAULT_MODEL_PRICING_USD_PER_1M: dict[str, ModelPricing] = {
    "gpt-5": ModelPricing(input_usd_per_1m=1.25, output_usd_per_1m=10.0, source="openai_default"),
    "gpt-5-mini": ModelPricing(input_usd_per_1m=0.25, output_usd_per_1m=2.0, source="openai_default"),
    "gpt-5-nano": ModelPricing(input_usd_per_1m=0.05, output_usd_per_1m=0.40, source="openai_default"),
}


def extract_token_usage(response: Any) -> Optional[TokenUsage]:
    """Extract token usage from common LangChain response shapes."""
    if isinstance(response, dict):
        return None

    usage = getattr(response, "usage_metadata", None)
    if not usage:
        metadata = getattr(response, "response_metadata", None) or {}
        usage = metadata.get("token_usage") or metadata.get("usage")

    if not usage:
        return None

    input_tokens = _first_int(usage, "input_tokens", "prompt_tokens")
    output_tokens = _first_int(usage, "output_tokens", "completion_tokens")
    total_tokens = _first_int(usage, "total_tokens")

    if total_tokens and not input_tokens and not output_tokens:
        input_tokens = total_tokens

    return TokenUsage(input_tokens=input_tokens, output_tokens=output_tokens)


def estimate_llm_cost(model_name: str, usage: TokenUsage) -> EstimatedCost:
    """Estimate USD cost from configured model pricing."""
    pricing = _pricing_for_model(model_name)
    if pricing is None:
        return EstimatedCost(
            input_cost_usd=0.0,
            output_cost_usd=0.0,
            total_cost_usd=0.0,
            pricing_source="not_configured",
        )

    input_cost = usage.input_tokens * pricing.input_usd_per_1m / 1_000_000
    output_cost = usage.output_tokens * pricing.output_usd_per_1m / 1_000_000
    return EstimatedCost(
        input_cost_usd=round(input_cost, 10),
        output_cost_usd=round(output_cost, 10),
        total_cost_usd=round(input_cost + output_cost, 10),
        pricing_source=pricing.source,
    )


def assert_llm_budget_available(model_name: str, agent_name: str, config: RunnableConfig | None = None) -> None:
    """Block an LLM call when monthly cost budget is already exhausted."""
    if not settings.LLM_COST_TRACKING_ENABLED or not settings.LLM_COST_BLOCKING_ENABLED:
        return
    if settings.LLM_MONTHLY_BUDGET_USD <= 0:
        return

    metadata = _metadata_from_config(config)
    user_id = _coerce_user_id(metadata.get("user_id"))
    start_at = _month_start()
    summary = _repository().summarize_usage(start_at=start_at, user_id=user_id)
    spent = float(summary["total_cost_usd"])

    if spent < settings.LLM_MONTHLY_BUDGET_USD:
        return

    llm_budget_exceeded_total.labels(model=model_name, agent_name=agent_name, budget_type="monthly").inc()
    logger.warning(
        "llm_monthly_budget_exceeded",
        model=model_name,
        agent_name=agent_name,
        user_id=user_id,
        spent_usd=spent,
        budget_usd=settings.LLM_MONTHLY_BUDGET_USD,
    )
    raise LLMBudgetExceededError("LLM monthly budget exceeded")


def record_llm_usage(
    response: BaseMessage,
    model_name: str,
    agent_name: str,
    config: RunnableConfig | None = None,
) -> Optional[LLMUsageRecord]:
    """Record token and cost usage in Prometheus and PostgreSQL."""
    if not settings.LLM_COST_TRACKING_ENABLED:
        return None

    usage = extract_token_usage(response)
    if usage is None:
        logger.debug("no_usage_metadata_in_response", model=model_name, agent_name=agent_name)
        return None

    cost = estimate_llm_cost(model_name, usage)
    llm_cost_usd_total.labels(model=model_name, agent_name=agent_name).inc(cost.total_cost_usd)
    llm_request_cost_usd.labels(model=model_name, agent_name=agent_name).observe(cost.total_cost_usd)

    if settings.LLM_REQUEST_BUDGET_USD > 0 and cost.total_cost_usd > settings.LLM_REQUEST_BUDGET_USD:
        llm_budget_exceeded_total.labels(model=model_name, agent_name=agent_name, budget_type="request").inc()
        logger.warning(
            "llm_request_budget_exceeded_after_call",
            model=model_name,
            agent_name=agent_name,
            request_cost_usd=cost.total_cost_usd,
            budget_usd=settings.LLM_REQUEST_BUDGET_USD,
        )

    metadata = _metadata_from_config(config)
    record = LLMUsageRecord(
        environment=settings.ENVIRONMENT.value,
        provider=_provider_from_model(model_name),
        model_name=_normalize_model_name(model_name),
        agent_name=agent_name,
        session_id=_coerce_str(metadata.get("session_id")),
        user_id=_coerce_user_id(metadata.get("user_id")),
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        total_tokens=usage.total_tokens,
        input_cost_usd=cost.input_cost_usd,
        output_cost_usd=cost.output_cost_usd,
        total_cost_usd=cost.total_cost_usd,
        pricing_source=cost.pricing_source,
    )
    saved = _repository().create_usage_record(record)
    logger.debug(
        "llm_usage_recorded",
        model=model_name,
        agent_name=agent_name,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        total_cost_usd=cost.total_cost_usd,
    )
    return saved


def _repository() -> LLMCostRepository:
    return LLMCostRepository(database_factory.get_session_maker())


def _pricing_for_model(model_name: str) -> Optional[ModelPricing]:
    normalized = _normalize_model_name(model_name)
    custom_pricing = _custom_pricing()
    if normalized in custom_pricing:
        return custom_pricing[normalized]
    return DEFAULT_MODEL_PRICING_USD_PER_1M.get(normalized)


def _custom_pricing() -> dict[str, ModelPricing]:
    if not settings.LLM_MODEL_PRICING_JSON:
        return {}

    try:
        raw = json.loads(settings.LLM_MODEL_PRICING_JSON)
    except json.JSONDecodeError as exc:
        logger.warning("llm_pricing_json_invalid", error=str(exc))
        return {}

    pricing: dict[str, ModelPricing] = {}
    for model_name, values in raw.items():
        if not isinstance(values, dict):
            continue
        input_price = values.get("input_usd_per_1m", values.get("input"))
        output_price = values.get("output_usd_per_1m", values.get("output"))
        if input_price is None or output_price is None:
            continue
        pricing[_normalize_model_name(model_name)] = ModelPricing(
            input_usd_per_1m=float(input_price),
            output_usd_per_1m=float(output_price),
            source="env",
        )
    return pricing


def _metadata_from_config(config: RunnableConfig | None) -> dict[str, Any]:
    if not isinstance(config, dict):
        return {}
    metadata = config.get("metadata")
    return metadata if isinstance(metadata, dict) else {}


def _first_int(values: dict[str, Any], *keys: str) -> int:
    for key in keys:
        value = values.get(key)
        if value is not None:
            return int(value)
    return 0


def _normalize_model_name(model_name: str) -> str:
    normalized = model_name.lower().strip()
    if ":" in normalized:
        normalized = normalized.split(":", 1)[1]
    return normalized


def _provider_from_model(model_name: str) -> str:
    if ":" in model_name:
        return model_name.split(":", 1)[0].lower()
    if model_name.lower().startswith("gpt-"):
        return "openai"
    return "unknown"


def _month_start() -> datetime:
    now = datetime.now(UTC)
    return datetime(year=now.year, month=now.month, day=1, tzinfo=UTC)


def _coerce_user_id(value: Any) -> Optional[int]:
    if value in (None, ""):
        return None
    return int(value)


def _coerce_str(value: Any) -> Optional[str]:
    if value in (None, ""):
        return None
    return str(value)
