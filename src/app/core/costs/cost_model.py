"""Database model for LLM token and cost usage."""

from datetime import datetime, UTC
from typing import Optional

from sqlmodel import Field, SQLModel


class LLMUsageRecord(SQLModel, table=True):
    """Persisted usage line for one LLM response."""

    __tablename__ = "llm_usage_record"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), index=True)

    environment: str = Field(default="development", max_length=40, index=True)
    provider: str = Field(default="openai", max_length=80, index=True)
    model_name: str = Field(max_length=160, index=True)
    agent_name: str = Field(max_length=160, index=True)
    session_id: Optional[str] = Field(default=None, max_length=120, index=True)
    user_id: Optional[int] = Field(default=None, index=True)

    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)

    input_cost_usd: float = Field(default=0.0, ge=0.0)
    output_cost_usd: float = Field(default=0.0, ge=0.0)
    total_cost_usd: float = Field(default=0.0, ge=0.0, index=True)
    pricing_source: str = Field(default="not_configured", max_length=120)
