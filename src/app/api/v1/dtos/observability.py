"""DTOs for observability endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field


class LLMUsageBucket(BaseModel):
    """Aggregated usage bucket grouped by model or agent."""

    input_tokens: int
    output_tokens: int
    total_tokens: int
    total_cost_usd: float
    model_name: str | None = None
    agent_name: str | None = None


class LLMCostSummaryResponse(BaseModel):
    """LLM usage and cost summary for the authenticated user."""

    start_at: datetime
    end_at: datetime
    user_id: int
    record_count: int
    input_tokens: int
    output_tokens: int
    total_tokens: int
    total_cost_usd: float
    monthly_budget_usd: float = Field(default=0.0)
    monthly_budget_remaining_usd: float | None = None
    blocking_enabled: bool
    pricing_configured: bool
    by_model: list[LLMUsageBucket]
    by_agent: list[LLMUsageBucket]
