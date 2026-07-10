"""Integration coverage for LLM cost tracking."""

from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from langchain_core.messages import AIMessage

from src.app.core.costs.cost_model import LLMUsageRecord
from src.app.core.costs.cost_service import estimate_llm_cost, extract_token_usage, record_llm_usage
from src.app.init import llm_cost_repository

pytestmark = pytest.mark.asyncio


async def test_extract_usage_and_estimate_default_cost():
    response = AIMessage(
        content="ok",
        usage_metadata={"input_tokens": 1000, "output_tokens": 500, "total_tokens": 1500},
    )

    usage = extract_token_usage(response)
    assert usage is not None
    assert usage.input_tokens == 1000
    assert usage.output_tokens == 500

    cost = estimate_llm_cost("gpt-5-mini", usage)
    assert cost.input_cost_usd == 0.00025
    assert cost.output_cost_usd == 0.001
    assert cost.total_cost_usd == 0.00125


async def test_record_llm_usage_persists_cost(client: AsyncClient, registered_user: dict):
    response = AIMessage(
        content="ok",
        usage_metadata={"input_tokens": 2000, "output_tokens": 1000, "total_tokens": 3000},
    )

    record = record_llm_usage(
        response,
        "gpt-5-nano",
        "Chatbot",
        {
            "metadata": {
                "user_id": registered_user["id"],
                "session_id": "cost-session",
            }
        },
    )

    assert record is not None
    assert record.user_id == registered_user["id"]
    assert record.session_id == "cost-session"
    assert record.input_tokens == 2000
    assert record.output_tokens == 1000
    assert record.total_cost_usd == 0.0005


async def test_llm_cost_summary_endpoint(client: AsyncClient, registered_user: dict, user_token: str):
    llm_cost_repository.create_usage_record(
        LLMUsageRecord(
            created_at=datetime.now(UTC),
            environment="test",
            provider="openai",
            model_name="gpt-5-mini",
            agent_name="Chatbot",
            session_id="summary-session",
            user_id=registered_user["id"],
            input_tokens=1000,
            output_tokens=500,
            total_tokens=1500,
            input_cost_usd=0.00025,
            output_cost_usd=0.001,
            total_cost_usd=0.00125,
            pricing_source="test",
        )
    )

    response = await client.get(
        "/api/v1/observability/llm-costs/summary",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == registered_user["id"]
    assert data["record_count"] == 1
    assert data["input_tokens"] == 1000
    assert data["output_tokens"] == 500
    assert data["total_cost_usd"] == 0.00125
    assert data["by_model"][0]["model_name"] == "gpt-5-mini"
    assert data["by_agent"][0]["agent_name"] == "Chatbot"


async def test_llm_cost_summary_requires_auth(client: AsyncClient):
    response = await client.get("/api/v1/observability/llm-costs/summary")

    assert response.status_code == 401
