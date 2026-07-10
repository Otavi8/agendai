"""Repository for LLM usage and cost records."""

from collections import defaultdict
from datetime import datetime
from typing import Any, Optional

from sqlmodel import Session, select

from src.app.core.common.logging import logger
from src.app.core.costs.cost_model import LLMUsageRecord


class LLMCostRepository:
    """Store and summarize LLM usage costs."""

    def __init__(self, session: Session):
        self.session = session

    def create_usage_record(self, record: LLMUsageRecord) -> Optional[LLMUsageRecord]:
        """Persist one usage record.

        Cost tracking must not break the agent runtime, so DB failures are logged
        and converted to ``None``.
        """
        try:
            self.session.add(record)
            self.session.commit()
            self.session.refresh(record)
            return record
        except Exception as exc:
            self.session.rollback()
            logger.warning("llm_usage_record_failed", error=str(exc))
            return None

    def list_usage_records(
        self,
        *,
        start_at: Optional[datetime] = None,
        end_at: Optional[datetime] = None,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        agent_name: Optional[str] = None,
    ) -> list[LLMUsageRecord]:
        """Return usage records matching optional filters."""
        statement = select(LLMUsageRecord)

        if start_at is not None:
            statement = statement.where(LLMUsageRecord.created_at >= start_at)
        if end_at is not None:
            statement = statement.where(LLMUsageRecord.created_at <= end_at)
        if user_id is not None:
            statement = statement.where(LLMUsageRecord.user_id == user_id)
        if session_id is not None:
            statement = statement.where(LLMUsageRecord.session_id == session_id)
        if agent_name is not None:
            statement = statement.where(LLMUsageRecord.agent_name == agent_name)

        statement = statement.order_by(LLMUsageRecord.created_at.desc())
        return list(self.session.exec(statement).all())

    def summarize_usage(
        self,
        *,
        start_at: Optional[datetime] = None,
        end_at: Optional[datetime] = None,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        agent_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Aggregate usage totals for API responses and dashboards."""
        records = self.list_usage_records(
            start_at=start_at,
            end_at=end_at,
            user_id=user_id,
            session_id=session_id,
            agent_name=agent_name,
        )

        by_model: dict[str, dict[str, float | int | str]] = defaultdict(
            lambda: {"model_name": "", "input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "total_cost_usd": 0.0}
        )
        by_agent: dict[str, dict[str, float | int | str]] = defaultdict(
            lambda: {"agent_name": "", "input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "total_cost_usd": 0.0}
        )

        input_tokens = 0
        output_tokens = 0
        total_tokens = 0
        total_cost_usd = 0.0

        for record in records:
            input_tokens += record.input_tokens
            output_tokens += record.output_tokens
            total_tokens += record.total_tokens
            total_cost_usd += record.total_cost_usd

            model_bucket = by_model[record.model_name]
            model_bucket["model_name"] = record.model_name
            model_bucket["input_tokens"] += record.input_tokens
            model_bucket["output_tokens"] += record.output_tokens
            model_bucket["total_tokens"] += record.total_tokens
            model_bucket["total_cost_usd"] += record.total_cost_usd

            agent_bucket = by_agent[record.agent_name]
            agent_bucket["agent_name"] = record.agent_name
            agent_bucket["input_tokens"] += record.input_tokens
            agent_bucket["output_tokens"] += record.output_tokens
            agent_bucket["total_tokens"] += record.total_tokens
            agent_bucket["total_cost_usd"] += record.total_cost_usd

        return {
            "record_count": len(records),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost_usd, 8),
            "by_model": [self._rounded_bucket(bucket) for bucket in by_model.values()],
            "by_agent": [self._rounded_bucket(bucket) for bucket in by_agent.values()],
        }

    @staticmethod
    def _rounded_bucket(bucket: dict[str, float | int | str]) -> dict[str, float | int | str]:
        rounded = dict(bucket)
        rounded["total_cost_usd"] = round(float(rounded["total_cost_usd"]), 8)
        return rounded
