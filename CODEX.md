# CODEX.md

Orientações para o Codex ao trabalhar neste repositório. Leia isto antes de fazer alterações.

## O Que Este Projeto É

Um **harness pronto para produção para agentes de IA**. Você escreve a lógica do agente; o harness fornece autenticação, memória de longo prazo, persistência de estado, rate limiting, guardrails, observabilidade e avaliação.

Stack: **LangGraph** (workflows de agentes), **FastAPI** (API assíncrona), **Langfuse** (tracing de LLM), **PostgreSQL + pgvector** (memória + checkpoints), **mem0ai** (memória de longo prazo), **MCP** (ferramentas), **Prometheus + Grafana** (monitoramento).

Um agente é um diretório autocontido em `src/app/agents/`. Todo o restante é infraestrutura compartilhada.

## Mapa do Repositório

```text
src/
├── app/
│   ├── main.py                # App FastAPI + lifespan (startup/shutdown)
│   ├── init.py                # Bootstrap de Langfuse, MCP e repositórios
│   ├── agents/                # Seus agentes vivem aqui
│   │   ├── chatbot/           # Agente de referência (mais simples)
│   │   ├── text_to_sql/       # Agente de referência (skills + tools)
│   │   ├── open_deep_research/# Agente de referência (multi-subgraph)
│   │   └── tools/             # Ferramentas compartilhadas (search, think)
│   ├── api/
│   │   ├── v1/                # Rotas versionadas (auth, chatbot, deep_research, text_to_sql)
│   │   │   └── dtos/          # Modelos Pydantic de request/response
│   │   ├── security/          # Auth JWT + rate limiter
│   │   └── metrics/           # Middleware de métricas HTTP Prometheus
│   └── core/
│       ├── common/config.py   # Settings (por env, fonte única de verdade)
│       ├── checkpoint/        # Wiring do LangGraph AsyncPostgresSaver
│       ├── context/           # Gerenciador de contexto + sumarizador
│       ├── db/                # Engine SQLModel + pool async
│       ├── guardrails/        # Filtro de conteúdo, PII, safety checks
│       ├── llm/               # Factory de LLM + helpers de retry
│       ├── mcp/               # Gerenciador de sessões MCP
│       ├── memory/            # Memória de longo prazo mem0
│       ├── middleware/        # Pipeline de middleware de agentes
│       ├── session/ · user/   # Modelos SQLModel, repositórios, DTOs
│       └── metrics/           # Métricas de LLM
├── cli/                       # Clientes de terminal para cada agente
├── evals/                     # Framework de avaliação baseado em métricas
└── mcp/server.py              # Servidor MCP de exemplo

frontend/                      # UI de chat React (Vite + React 19 + TS + Tailwind v4)
├── src/lib/api.ts             # Cliente de API tipado + streaming SSE
├── src/context/AuthContext.tsx# Auth em dois tokens (token de usuário -> token de sessão)
└── src/components/            # LoginScreen, ChatScreen, Sidebar, MessageBubble, Composer
```

## Comandos de Desenvolvimento

```bash
make install              # uv sync
make db-up                # inicia APENAS o Postgres (pgvector) no Docker
make dev                  # roda a API em :8000 (reload), lê .env.development
uv run pytest tests/      # roda os testes
make lint                 # ruff check
make format               # ruff format
make eval                 # avaliação interativa

make docker-compose-up ENV=development    # stack completa (API + db + Prometheus + Grafana + cAdvisor)
```

Swagger: `http://localhost:8000/docs` · Grafana: `http://localhost:3000` (admin/admin) · Prometheus: `http://localhost:9090`

A configuração fica em `.env.<environment>` (development/staging/production). Copie `.env.example` para `.env.development` e preencha `OPENAI_API_KEY`, `JWT_SECRET_KEY`, `LANGFUSE_*`. Todas as settings são lidas em `src/app/core/common/config.py`; esse arquivo é a fonte única de verdade da configuração.

### Frontend (`frontend/`)

```bash
cd frontend && npm install     # primeira vez
npm run dev                    # http://localhost:5173 (proxy /api -> :8000)
npm run build                  # type-check (tsc -b) + bundle
```

UI de chat React para o agente `chatbot` (auth, sidebar de sessões, streaming). Fala com o backend apenas via proxy do Vite (`/api/*`). Modelo de dois tokens: o token de usuário cria/lista sessões; o token de sessão é exigido pelo chat. Veja o slash command `/frontend` e `frontend/README.md`.

### Rodando no Windows

`make`/`bash` são Linux/Mac. No Windows, use `.\dev.ps1` na raiz do repositório. Ele inicia o Postgres, força `SelectorEventLoop` (o pool async do psycopg não funciona com o `ProactorEventLoop` padrão) e roda a API via `run_local.py`. `uvloop` é intencionalmente excluído em win32.

## Como Criar um Novo Agente

1. Crie `src/app/agents/<name>/` com:
   - `__init__.py`: helper `load_system_prompt()`
   - `agent_<name>.py`: classe do agente (compila um grafo LangGraph)
   - `system.md`: template de prompt. Suporta placeholders `{long_term_memory}` e `{current_date_and_time}`.
   - `tools/`: ferramentas customizadas opcionais, exportadas como uma lista `tools`
2. Adicione um DTO em `src/app/api/v1/dtos/` e uma rota em `src/app/api/v1/`.
3. Registre o router em `src/app/api/v1/api.py`.
4. Adicione uma entrada de rate limit em `config.py` (`RATE_LIMIT_ENDPOINTS`) e uma env var se necessário.
5. Invoque via `agent.agent_invoke()` / `agent.agent_invoke_stream()`.

Use `src/app/agents/chatbot/` + `src/app/api/v1/chatbot.py` como referência canônica. Há um slash command `/new-agent` que faz o scaffold para você.

## Convenções Inegociáveis

1. **Todas as rotas têm decorator de rate limit**: `@limiter.limit(...)` usando `RATE_LIMIT_ENDPOINTS`.
2. **Todas as operações de LLM têm tracing** pelo Langfuse (passe o callback handler).
3. **Async em tudo** para banco e I/O externo; nunca bloqueie o event loop.
4. **Apenas logging estruturado** (`structlog`): nomes de eventos em `lowercase_with_underscores`, variáveis passadas como kwargs, **nunca f-strings** dentro do evento. Use `logger.exception()` para erros, preservando tracebacks.
5. **Retries usam `tenacity`** com exponential backoff.
6. **Saída de console/CLI usa `rich`.**
7. **Faça cache apenas de respostas bem-sucedidas**, nunca de erros.
8. **Todos os imports no topo do arquivo**; nunca dentro de funções ou classes.
9. **Acesso a banco é async** e usa connection pool.
10. **Type hints + modelos Pydantic** em todo endpoint; prefira objetos a dicts crus (RORO).

### Estilo de Tratamento de Erros

Guard clauses primeiro, retornos antecipados para condições de erro e caminho feliz por último. Use `HTTPException` com status code adequado para erros esperados; middleware global para erros inesperados.

## Armadilhas Comuns

- f-strings em eventos do `structlog`; imports dentro de funções.
- Decorator de rate limit ausente em uma rota; tracing Langfuse ausente em chamada de LLM.
- `logger.error()` em vez de `logger.exception()` para exceções capturadas.
- I/O bloqueante sem `async`; secrets/chaves hardcoded; type hints ausentes.

## Fluxo de Planejamento

Para qualquer tarefa não trivial, escreva primeiro um plano em `.codex/plans/<task-name>.md` como checkboxes no estilo GitHub (`- [ ] etapa`), com marcador de complexidade (Simples / Médio / Complexo) e ao menos uma validação por item. Atualize `- [ ]` para `- [x]` conforme concluir cada etapa. O slash command `/plan` faz isso.

## Notas para o Codex

- Este repositório é desenvolvido com **Codex**, não Cursor. As regras do projeto vivem neste arquivo e em `.codex/`. `AGENTS.md` é um espelho genérico mantido para outras ferramentas.
- Host Windows: o shell principal é PowerShell; uma ferramenta Bash também está disponível. `make`/`uv` usam o `.venv`.
- `schema.sql` na raiz é DDL legado no estilo SQLite. O schema real é criado pelo SQLModel (`SQLModel.metadata.create_all`) e pelo checkpointer do LangGraph no startup. Não dependa dele.
