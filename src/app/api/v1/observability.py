"""Operational observability endpoints."""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Query, Request

from src.app.api.security.limiter import limiter
from src.app.api.v1.auth import get_current_user
from src.app.api.v1.dtos.observability import LLMCostSummaryResponse
from src.app.core.common.config import settings
from src.app.core.costs.cost_service import DEFAULT_MODEL_PRICING_USD_PER_1M
from src.app.core.user.user_model import User
from src.app.init import llm_cost_repository

router = APIRouter()


@router.get("/llm-costs/summary", response_model=LLMCostSummaryResponse)
@limiter.limit(settings.RATE_LIMIT_ENDPOINTS["observability"][0])
async def get_llm_cost_summary(
    request: Request,
    days: int = Query(default=30, ge=1, le=366),
    user: User = Depends(get_current_user),
) -> LLMCostSummaryResponse:
    """Return token and estimated cost summary for the authenticated user."""
    end_at = datetime.now(UTC)
    start_at = end_at - timedelta(days=days)
    summary = llm_cost_repository.summarize_usage(start_at=start_at, end_at=end_at, user_id=user.id)
    remaining = None
    if settings.LLM_MONTHLY_BUDGET_USD > 0:
        remaining = round(max(settings.LLM_MONTHLY_BUDGET_USD - float(summary["total_cost_usd"]), 0.0), 8)

    return LLMCostSummaryResponse(
        start_at=start_at,
        end_at=end_at,
        user_id=user.id,
        record_count=summary["record_count"],
        input_tokens=summary["input_tokens"],
        output_tokens=summary["output_tokens"],
        total_tokens=summary["total_tokens"],
        total_cost_usd=summary["total_cost_usd"],
        monthly_budget_usd=settings.LLM_MONTHLY_BUDGET_USD,
        monthly_budget_remaining_usd=remaining,
        blocking_enabled=settings.LLM_COST_BLOCKING_ENABLED,
        pricing_configured=bool(settings.LLM_MODEL_PRICING_JSON or DEFAULT_MODEL_PRICING_USD_PER_1M),
        by_model=summary["by_model"],
        by_agent=summary["by_agent"],
    )
