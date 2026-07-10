from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig

from src.app.core.common.logging import logger
from src.app.core.costs.cost_service import assert_llm_budget_available, extract_token_usage, record_llm_usage
from src.app.core.metrics.metrics import llm_inference_duration_seconds, tokens_in_counter, tokens_out_counter


async def model_invoke_with_metrics(
    model,
    model_input: LanguageModelInput,
    model_name: str,
    agent_name: str,
    config: RunnableConfig | None = None
):
    assert_llm_budget_available(model_name, agent_name, config)
    with llm_inference_duration_seconds.labels(model=model_name, agent_name=agent_name).time():
        response = await model.ainvoke(model_input, config)
    record_token_usage(response, model_name, agent_name)
    record_llm_usage(response, model_name, agent_name, config)
    return response


def record_token_usage(response: BaseMessage, model: str, agent_name: str) -> None:
    """Extract token usage from an LLM response and increment Prometheus counters.

    Uses LangChain's standardised ``usage_metadata`` attribute which is
    populated by all major providers (OpenAI, Anthropic, Google, etc.).
    """
    usage = extract_token_usage(response)
    if not usage:
        logger.debug("no_usage_metadata_in_response", model=model, agent_name=agent_name)
        return

    tokens_in_counter.labels(agent_name=agent_name).inc(usage.input_tokens)
    tokens_out_counter.labels(agent_name=agent_name).inc(usage.output_tokens)

    logger.debug(
        "llm_token_usage_recorded",
        model=model,
        agent_name=agent_name,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
    )
