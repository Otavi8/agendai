# Estrutura do Projeto

Este repositório será usado como motor/template para criar novos agentes. A ideia é preservar a infraestrutura comum e trocar ou adicionar agentes conforme o produto de IA que será construído.

## Visão Geral

O projeto é um agent harness: uma aplicação pronta para produção ao redor de agentes de IA.

Ele entrega:

- API FastAPI com autenticação, sessões e rate limiting.
- Agentes LangGraph/Deep Agents em `src/app/agents/`.
- Memória de longo prazo com mem0 + pgvector.
- Persistência de conversas via checkpointing.
- Guardrails de entrada e saída.
- Observabilidade com Langfuse, Prometheus e Grafana.
- Frontend React/Vite para chat.
- Evals para medir qualidade de respostas.
- Estrutura `.codex/` para guiar o Codex na criação de novos agentes.

## Raiz do Projeto

| Caminho | Função |
|---------|--------|
| `README.md` | Visão geral do projeto, quick start, capacidades e referência de API. |
| `CODEX.md` | Guia principal para o Codex trabalhar neste repo: mapa, comandos, convenções e fluxo de criação de agentes. |
| `AGENTS.md` | Guia genérico para agentes de IA, mantido para compatibilidade com outras ferramentas. |
| `CONTEXT.md` | Arquivo vivo para descobrir e registrar a ideia do produto antes de codar. |
| `pyproject.toml` | Manifesto Python: dependências, versão do pacote, configuração de lint/testes. |
| `uv.lock` | Lockfile do `uv`, garantindo versões reproduzíveis das dependências Python. |
| `Makefile` | Atalhos de desenvolvimento, Docker, testes, lint e evals. |
| `dev.ps1` | Fluxo local para Windows: sobe DB e roda API de forma compatível com PowerShell. |
| `run_local.py` | Entrypoint local para rodar a API no Windows com event loop adequado. |
| `Dockerfile` | Build da imagem da API. |
| `docker-compose.yml` | Stack local com API, Postgres, Prometheus, Grafana e cAdvisor. |
| `.env.example` | Template de variáveis de ambiente. |
| `.gitignore` | Regras do Git para ignorar envs, caches, planos locais e artefatos. |
| `.dockerignore` | Arquivos que não entram no build Docker. |
| `schema.sql` | DDL legado; o schema real é criado pelo SQLModel/checkpointer. |
| `skills-lock.json` | Registro das skills disponíveis/baixadas para o fluxo de agente. |
| `LICENSE` | Licença do projeto. |

## `.codex/`

Configuração do Codex para operar este repositório como um motor de agentes.

| Caminho | Função |
|---------|--------|
| `.codex/settings.json` | Permissões e allowlist migradas da estrutura anterior. |
| `.codex/agents/harness-reviewer.md` | Subagente revisor que checa diffs contra as convenções obrigatórias do repo. |
| `.codex/commands/` | Comandos reutilizáveis para tarefas comuns: banco, frontend, novo agente, plano e execução local. |
| `.codex/plans/` | Pasta para planos de tarefas não triviais. |
| `.codex/skills/` | Biblioteca de skills usadas pelo Codex para LangChain, LangGraph, Deep Agents, RAG, middleware, persistência e execução paralela. |

### Commands

| Comando | Uso |
|---------|-----|
| `db.md` | Gerenciar o Postgres local: subir, derrubar, logs, psql, reset. |
| `frontend.md` | Trabalhar no frontend React: dev, build, abas de agente, sessões. |
| `new-agent.md` | Scaffold de novo agente com pasta, DTO, rota, rate limit e registro no router. |
| `plan.md` | Criar plano em `.codex/plans/` antes de tarefas maiores. |
| `run.md` | Subir banco + API localmente e validar `/health`. |

### Skills do Codex

| Skill | Para que serve |
|-------|----------------|
| `ecosystem-primer` | Ponto de partida para escolher LangChain, LangGraph, Deep Agents ou composição híbrida. |
| `langchain-dependencies` | Dependências, versões, ambiente e pacotes Python/TypeScript para LangChain/LangGraph. |
| `langchain-fundamentals` | Criação de agentes LangChain, tools, middleware e structured output. |
| `langchain-middleware` | Human-in-the-loop, middleware customizado, approval workflows e output estruturado. |
| `langchain-rag` | Pipeline RAG: loaders, splitters, embeddings, vector stores e retrieval. |
| `langgraph-cli` | Uso da CLI LangGraph: scaffold, dev, build, up e deploy. |
| `langgraph-fundamentals` | StateGraph, state schemas, nós, arestas, `Command`, `Send`, invoke e stream. |
| `langgraph-human-in-the-loop` | Pausas para aprovação humana, `interrupt()`, `Command(resume=...)` e workflows de validação. |
| `langgraph-persistence` | Checkpointers, `thread_id`, histórico, time travel, Store e persistência em subgraphs. |
| `deep-agents-core` | Fundamentos de Deep Agents: `create_deep_agent()`, formato `SKILL.md` e arquitetura. |
| `deep-agents-memory` | Backends de memória/filesystem para Deep Agents: State, Store, Filesystem e Composite. |
| `deep-agents-orchestration` | Subagentes, planejamento, `TodoList` e aprovação humana em Deep Agents. |
| `managed-deep-agents` | Criação, deploy e operação de Managed Deep Agents no LangSmith. |
| `swarm` | Execução paralela/multiagente em lote, agregação, chaining e filtros. |

## `apresentação/`

Material visual para estudar e apresentar a ideia de agent harness.

| Arquivo | Função |
|---------|--------|
| `apostila_criando_agents.html` | Apostila navegável em HTML, com páginas de estudo, atalhos e layout claro. |

Este arquivo é útil para estudar:

- O conceito de harness.
- Por que IA precisa de estrutura ao redor do modelo.
- O ciclo de vida de um projeto de agente.
- Como este repositório se organiza como motor reutilizável.
- Como criar agents usando `.codex/`, Skills, ADRs, scripts, rotas e agentes de referência.

## `assets/`

Arquivos visuais usados na documentação e apresentação.

| Arquivo | Função |
|---------|--------|
| `traces.png` | Exemplo de trace Langfuse. |
| `langfuse-dashboard.png` | Dashboard Langfuse com custos/uso/traces. |
| `graphana_metrics.png` | Dashboard Grafana/Prometheus. |
| `ai-agent-harness-presentation.pptx` | Versão PPTX da apresentação original. |

## `docs/`

Documentação de estudo, requisitos e evolução do projeto.

| Arquivo/Pasta | Função |
|---------------|--------|
| `ARTICLE.md` | Artigo explicando a arquitetura de um agent harness pronto para produção. |
| `middleware-for-agent-harness.md` | Documento focado no middleware de agentes e nos hooks do pipeline. |
| `PROJECT_REPORT.md` | Relatório do estado do projeto e próximos caminhos de produto. |
| `PERGUNTAS_PROJETO.md` | Roteiro de perguntas para descobrir requisitos no estilo grill-with-docs. |
| `ESTRUTURA_PROJETO.md` | Este mapa por pastas. |
| `adr/` | Pasta para Architecture Decision Records, decisões importantes do projeto. |

## `frontend/`

Frontend React + Vite + TypeScript + Tailwind para conversar com os agentes.

| Caminho | Função |
|---------|--------|
| `frontend/package.json` | Dependências e scripts (`dev`, `build`, `preview`). |
| `frontend/vite.config.ts` | Config do Vite; faz proxy `/api/*` para backend em `localhost:8000`. |
| `frontend/index.html` | HTML base do app. |
| `frontend/src/main.tsx` | Entry point React. |
| `frontend/src/App.tsx` | Decide qual tela renderizar conforme autenticação. |
| `frontend/src/index.css` | Estilos globais/Tailwind. |
| `frontend/src/context/AuthContext.tsx` | Fluxo de auth em dois tokens: usuário e sessão. |
| `frontend/src/lib/api.ts` | Cliente tipado da API e streaming SSE. |
| `frontend/src/lib/types.ts` | Tipos TypeScript espelhando DTOs do backend. |
| `frontend/src/components/LoginScreen.tsx` | Tela de cadastro/login. |
| `frontend/src/components/ChatScreen.tsx` | Tela principal de chat, histórico, envio e sessões. |
| `frontend/src/components/Composer.tsx` | Caixa de entrada de mensagem. |
| `frontend/src/components/MessageBubble.tsx` | Renderização de mensagens. |
| `frontend/src/components/AgentActivity.tsx` | Indicador/atividade do agente. |
| `frontend/src/components/SourcesPanel.tsx` | Painel para conectar banco e autorizar pasta para o data agent. |

O frontend fala com o backend via:

- `/api/v1/auth/*` para usuário e sessão.
- `/api/v1/chatbot/*` para chat.
- `/api/v1/data-agent/*` para conectar fontes e consultar dados.
- Futuramente pode ganhar abas para novos agentes.

## `src/`

Código principal Python.

### `src/app/`

Aplicação FastAPI.

| Arquivo/Pasta | Função |
|---------------|--------|
| `main.py` | Cria o app FastAPI, lifespan, métricas, middlewares e router principal. |
| `init.py` | Inicialização de dependências compartilhadas como Langfuse, MCP e repositories. |
| `api/` | Rotas HTTP, autenticação, rate limiting e métricas HTTP. |
| `agents/` | Implementações dos agentes. |
| `core/` | Infraestrutura compartilhada do harness. |

### `src/app/api/`

Camada HTTP.

| Caminho | Função |
|---------|--------|
| `api/v1/api.py` | Router principal de versão; registra `auth`, `chatbot`, `deep-research`, `text-to-sql`, `data-agent` e `/health`. |
| `api/v1/auth.py` | Registro, login, criação/listagem/renomeação/exclusão de sessões. |
| `api/v1/chatbot.py` | Endpoints do chatbot: chat, stream, histórico e limpeza. |
| `api/v1/deep_research.py` | Endpoints de pesquisa profunda, normal e streaming. |
| `api/v1/text_to_sql.py` | Endpoint de consulta text-to-SQL. |
| `api/v1/data_agent.py` | Endpoints para conectar banco, autorizar pasta, consultar e ver status de fontes. |
| `api/v1/dtos/` | Modelos Pydantic de request/response. |
| `api/security/auth.py` | JWT, hash de senha e dependências de autenticação. |
| `api/security/limiter.py` | Configuração do slowapi/rate limiting. |
| `api/metrics/` | Métricas HTTP e middleware Prometheus. |
| `api/logging_context.py` | Contexto de logging por request. |

### `src/app/agents/`

Onde novos agentes devem nascer.

| Agente/Pasta | Função |
|--------------|--------|
| `chatbot/` | Agente de chat de referência com LangGraph explícito, memória, tools, guardrails e streaming. |
| `text_to_sql/` | Agente Deep Agents para transformar linguagem natural em SQL sobre banco Chinook. |
| `open_deep_research/` | Agente de pesquisa profunda com supervisor, researcher subgraph, tool loop e relatório final. |
| `data_agent/` | Agente para consultar fontes autorizadas, como banco read-only e pastas em sandbox. |
| `tools/` | Ferramentas compartilhadas como search, DuckDuckGo e think tool. |

#### Skills do `text_to_sql`

| Skill | Uso |
|-------|-----|
| `schema-exploration` | Descobrir tabelas, colunas, tipos e relacionamentos do banco. |
| `query-writing` | Escrever e executar consultas SQL simples, JOINs, agregações e análises. |

### `src/app/core/`

Infraestrutura compartilhada do harness.

| Pasta | Função |
|-------|--------|
| `common/` | Configuração, logging, utilitários, modelos base e limites de tokens. |
| `db/` | Engine SQLModel, connection pool, acesso read-only e helpers de banco. |
| `checkpoint/` | Checkpointer LangGraph/Postgres e limpeza de threads. |
| `context/` | Gerenciamento de contexto: offloading de ferramentas, trimming e sumarização. |
| `guardrails/` | Filtro de conteúdo, detecção/redação de PII, safety check e nós LangGraph. |
| `llm/` | Utilitários de LLM. |
| `mcp/` | Gerenciamento de sessões MCP e carregamento de tools MCP. |
| `memory/` | Memória de longo prazo com mem0. |
| `metrics/` | Métricas Prometheus de LLM, tokens, duração e tools. |
| `middleware/` | `AgentPipeline`, `AgentMiddleware` e middlewares de logging, erro, memória, guardrails, trimming e sumarização. |
| `sandbox/` | Sandbox Docker e registry para execução controlada. |
| `session/` | Modelo, DTO e repository de sessões. |
| `user/` | Modelo, DTO e repository de usuários. |

## `src/cli/`

Clientes de terminal para usar os agentes sem frontend.

| Arquivo | Função |
|---------|--------|
| `api_client.py` | Cliente CLI para autenticar e conversar com o chatbot. |
| `deep_research_client.py` | Cliente CLI para o agente de pesquisa profunda. |
| `text_to_sql_client.py` | Cliente CLI para o agente text-to-SQL. |

## `src/evals/`

Framework de avaliação de respostas da LLM.

| Caminho | Função |
|---------|--------|
| `main.py` | Entrypoint das avaliações. |
| `evaluator.py` | Busca traces, executa métricas e envia scores. |
| `helpers.py` | Helpers para extrair input/output e lidar com traces. |
| `schemas.py` | Schemas Pydantic para scores e relatórios. |
| `metrics/prompts/*.md` | Prompts de métricas: conciseness, hallucination, helpfulness, relevancy, toxicity. |

## `src/mcp/`

Servidor MCP de exemplo.

| Arquivo | Função |
|---------|--------|
| `server.py` | Servidor MCP sample para expor ferramentas ao agente. |

## `observability/`

Configuração de monitoramento.

| Caminho | Função |
|---------|--------|
| `prometheus/prometheus.yml` | Configuração de scrape do Prometheus. |
| `grafana/datasources/datasources.yml` | Fonte de dados Grafana. |
| `grafana/dashboards/dashboards.yml` | Provisionamento de dashboards. |
| `grafana/dashboards/json/llm_latency.json` | Dashboard JSON de observabilidade de LLM. |

## `scripts/`

Scripts operacionais para Docker e banco.

| Arquivo/Pasta | Função |
|---------------|--------|
| `build-docker.sh` | Build de imagem. |
| `run-docker.sh` | Execução Docker. |
| `stop-docker.sh` | Parada de containers. |
| `logs-docker.sh` | Logs Docker. |
| `set_env.sh` | Setup de variáveis. |
| `ensure-db-user.sh` | Garante usuário de banco. |
| `docker-entrypoint.sh` | Entrypoint usado pela imagem Docker. |
| `postgres/init/01-init-extensions.sql` | Inicialização do Postgres com extensão pgvector. |

## `tests/`

Testes de integração.

| Arquivo | Função |
|---------|--------|
| `conftest.py` | Fixtures compartilhadas dos testes de integração. |
| `test_auth.py` | Testa autenticação e sessões. |
| `test_chatbot.py` | Testa endpoints/fluxo do chatbot. |
| `test_deep_research.py` | Testa agente de pesquisa profunda. |
| `test_text_to_sql.py` | Testa agente text-to-SQL. |
| `test_guardrails.py` | Testa filtros, PII e safety. |
| `test_health.py` | Testa endpoint de saúde. |

## Como Usar Este Motor Para Criar Novos Agentes

1. Preencha `CONTEXT.md` usando as perguntas de `docs/PERGUNTAS_PROJETO.md`.
2. Crie ADRs em `docs/adr/` para decisões importantes.
3. Use `.codex/commands/new-agent.md` como guia para scaffold.
4. Crie a pasta do agente em `src/app/agents/<novo_agente>/`.
5. Adicione DTO em `src/app/api/v1/dtos/`.
6. Adicione rota em `src/app/api/v1/`.
7. Registre a rota em `src/app/api/v1/api.py`.
8. Configure rate limit em `src/app/core/common/config.py`.
9. Exponha o agente no frontend se fizer sentido.
10. Adicione testes e evals para o comportamento esperado.
