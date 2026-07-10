# Observabilidade e controle de custos de LLM

O AgendAI registra uso de LLM em tres camadas:

- Langfuse: traces, sessoes e custos detalhados quando `LANGFUSE_PUBLIC_KEY` e `LANGFUSE_SECRET_KEY` estao configuradas.
- Prometheus/Grafana: metricas operacionais de tokens, custo estimado, latencia, erros, ferramentas e guardrails.
- PostgreSQL: historico em `llm_usage_record` para consultas por usuario, sessao, agente e modelo.

## Variaveis de ambiente

```env
LLM_COST_TRACKING_ENABLED=true
LLM_COST_BLOCKING_ENABLED=false
LLM_MONTHLY_BUDGET_USD=0
LLM_REQUEST_BUDGET_USD=0
LLM_MODEL_PRICING_JSON=
```

- `LLM_COST_TRACKING_ENABLED`: liga/desliga o registro de custo.
- `LLM_COST_BLOCKING_ENABLED`: quando `true`, bloqueia novas chamadas se o orcamento mensal ja foi atingido.
- `LLM_MONTHLY_BUDGET_USD`: limite mensal em USD. `0` significa sem limite.
- `LLM_REQUEST_BUDGET_USD`: emite alerta de log/metrica quando uma chamada individual passa do valor. `0` desliga o alerta.
- `LLM_MODEL_PRICING_JSON`: sobrescreve precos por modelo, em USD por 1M tokens.

Exemplo:

```env
LLM_MODEL_PRICING_JSON={"gpt-5-mini":{"input_usd_per_1m":0.25,"output_usd_per_1m":2.0},"gpt-5-nano":{"input_usd_per_1m":0.05,"output_usd_per_1m":0.4}}
```

## API

Resumo autenticado do usuario:

```http
GET /api/v1/observability/llm-costs/summary?days=30
Authorization: Bearer <user_token>
```

O retorno inclui tokens, custo total, agrupamento por modelo/agente e saldo de orcamento quando configurado.

## Metricas Prometheus

- `llm_tokens_in_total`
- `llm_tokens_out_total`
- `llm_cost_usd_total`
- `llm_request_cost_usd`
- `llm_budget_exceeded_total`
- `llm_inference_duration_seconds`
- `llm_stream_duration_seconds`

## Grafana

O dashboard provisionado em `observability/grafana/dashboards/json/llm_latency.json` inclui paineis de custo estimado. Acesse:

```text
http://IP_DA_VPS:3000/d/llm-latency/llm-observability
```

Usuario/senha padrao no compose: `admin/admin`.
