# Relatório do Projeto: Agent Harness (template pronto para produção)

_Gerado em 2026-07-03. Cobre: o que mudou nesta sessão, o que o projeto é e faz, e para onde levá-lo para uso real com alto ROI._

---

## 1. O Que Foi Alterado Nesta Sessão

Objetivo: migrar o repositório do Cursor para o Codex, adicionar um serviço Docker de Postgres de primeira classe e documentar tudo em `.codex/` e `CODEX.md`.

### Adicionado

| Caminho | Finalidade |
|---------|------------|
| `CODEX.md` | Orientação principal para o Codex: mapa do projeto, comandos de dev, 10 convenções, como criar um agente e armadilhas. |
| `.codex/settings.json` | Allowlist de permissões migrada da configuração anterior do assistente. |
| `.codex/commands/new-agent.md` | `/new-agent`: cria o scaffold de um agente completo (pacote + rota + DTO + rate limit). |
| `.codex/commands/plan.md` | `/plan`: escreve um plano com checkboxes em `.codex/plans/` antes de codar. |
| `.codex/commands/run.md` | `/run`: sobe DB + API e verifica `/health`. |
| `.codex/commands/db.md` | `/db up\|down\|logs\|psql\|reset`: gerencia o Postgres local. |
| `.codex/agents/harness-reviewer.md` | Subagente que revisa diffs contra as convenções do repositório. |
| `.codex/skills/` | Biblioteca de skills migrada da configuração anterior do assistente. |
| `.codex/plans/.gitkeep` | Local dos planos de tarefas. |
| `scripts/postgres/init/01-init-extensions.sql` | Habilita a extensão `pgvector` na primeira inicialização do banco. |
| `.env.development` | Config local de dev (gitignored) para `make db-up` + `make dev` funcionarem direto. |
| `docs/PROJECT_REPORT.md` | Este relatório. |

### Modificado

- **`docker-compose.yml`**: serviço `db` reconstruído; container nomeado `agent-harness-db`, env com defaults seguros (não falha mais sem `.env`), script de init do pgvector montado, `start_period` adicionado ao healthcheck e chave obsoleta `version:` removida.
- **`Makefile`**: novos targets `db-up` (espera ficar healthy), `db-down`, `db-logs`, `db-reset` + help.
- **`.gitignore`**: deixou de ignorar tudo em `/.codex/`; agora versiona a configuração compartilhada e ignora apenas `settings.local.json` e `plans/*`.
- **`AGENTS.md`**: caminho de plano atualizado de `.agent/plans/` para `.codex/plans/`.

### Removido

- **`.cursor/`** (rules + gitignore): Cursor não é mais usado; suas regras foram incorporadas ao `CODEX.md`.

### Como Rodar Agora

```bash
make install     # uv sync
make db-up       # Postgres + pgvector, espera ficar healthy
# preencha OPENAI_API_KEY e JWT_SECRET_KEY em .env.development
make dev         # API em http://localhost:8000 (Swagger em /docs)
```

---

## 2. O Que Este Projeto É

Um **harness para executar agentes de IA em produção**. Você escreve a lógica do agente; o harness fornece a infraestrutura que todo agente sério precisa e que ninguém quer reconstruir:

- **Camada de API**: FastAPI (async, uvloop), autenticação JWT com gerenciamento de múltiplas sessões, rate limiting por endpoint (slowapi), streaming SSE.
- **Memória e estado**: memória semântica de longo prazo por usuário (mem0ai + pgvector) com atualizações em background sem bloqueio; estado da conversa persistido via checkpoints `AsyncPostgresSaver` do LangGraph.
- **Observabilidade**: tracing Langfuse em toda chamada de LLM; métricas Prometheus; dashboards Grafana prontos; logging estruturado com `structlog` e binding de contexto de request/sessão/usuário.
- **Segurança**: módulo de guardrails (content filter, detecção de PII, safety checks) e pipeline de middleware de agentes (tratamento de erro, logging, sumarização, trimming de mensagens, memória).
- **Ferramentas**: ferramentas internas (web search, "think") mais suporte a cliente MCP (múltiplos servidores, reconexão automática, degradação graciosa) e servidor MCP de exemplo.
- **Avaliação**: framework de eval baseado em métricas dirigido por traces do Langfuse; métricas são arquivos markdown (relevancy, helpfulness, conciseness, hallucination, toxicity).
- **DevOps**: stack Docker Compose (Postgres, Prometheus, Grafana, cAdvisor), configs por ambiente, Makefile, GitHub Actions.

### Como Está Organizado

Um agente é um **diretório autocontido** em `src/app/agents/`. Três referências acompanham o projeto: `chatbot` (mais simples), `text_to_sql` (skills + tools), `open_deep_research` (supervisor/researcher com multi-subgraph). O restante de `src/app/core/` é infraestrutura compartilhada conectada ao agente.

### Ciclo de Vida de Request (chat)

```text
Client -> rota FastAPI (JWT auth + rate limit)
       -> carrega memória de longo prazo (mem0/pgvector) -> monta prompt
       -> agente LangGraph (estado com checkpoint, tools/MCP) com tracing Langfuse
       -> faz stream/retorna resposta
       -> background: extrai e salva novas memórias (asyncio task, sem bloqueio)
Prometheus coleta /metrics -> dashboards Grafana
```

---

## 3. Para Onde Levar: Direções de Alto ROI

O valor do template é que os 80% caros e pouco glamourosos (auth, memória, tracing, persistência, rate limits, evals) já estão prontos. O caminho mais rápido para algo "real e lucrativo" é colocar um **agente específico de domínio** em `src/app/agents/` e vender o resultado, não a tecnologia. Candidatos por esforço versus retorno:

**A. Copiloto vertical de suporte/operações (mais rápido para receita).**
Conecte o agente à base de conhecimento de uma empresa + algumas ferramentas (consulta de pedido, abertura de ticket) via MCP. O harness já entrega memória por usuário (lembra cada cliente), tracing (você prova qualidade ao comprador) e guardrails (PII). Venda como SaaS por assento ou por resolução. O agente `text_to_sql` é um ponto de partida funcional para ferramentas internas de "pergunte aos seus dados".

**B. Produto de analytics / "chat com seu banco".**
`text_to_sql` + a skill de exploração de schema já são grande parte de um assistente de BI self-service. Adicione auth por linha e cache de resultado (cache apenas de consultas bem-sucedidas, convenção #7) e você terá uma ferramenta interna vendável de analytics. O ROI é alto porque substitui idas e vindas com analistas.

**C. Automação de pesquisa / due diligence.**
`open_deep_research` (subgraphs supervisor + researcher) já faz pesquisa web em múltiplas etapas com uma ferramenta `think`. Empacote para um nicho (jurídico, mercado, inteligência competitiva) com enforcement de citações pelas métricas de eval existentes (hallucination, relevancy). Cobre por relatório.

**D. Plataforma de hosting multi-tenant de agentes.**
O harness está perto de um "Fly.io para agentes". Para chegar lá: adicione isolamento de tenants (schema por tenant ou row-level security no Postgres), medição de uso (você já emite métricas Prometheus; cobre por duração/tokens de inferência LLM) e um registry self-service de agentes. Mais esforço, mas com uma defesa competitiva real.

### Próximos Passos Concretos para Produção

1. **Custo e billing**: emita token/custo por request no Prometheus e mostre um dashboard de custo por tenant no Grafana.
2. **Arrumar a história do schema**: `schema.sql` é DDL legado SQLite; padronize em migrations Alembic para tabelas da app, garantindo deploys reprodutíveis.
3. **Gate de eval no CI**: rode o framework de eval em um conjunto fixo de traces no GitHub Actions e falhe o build se hallucination/relevancy regredir.
4. **Endurecer guardrails**: o middleware de guardrail já existe; conecte-o em todo pipeline de agente e adicione moderação de saída antes de respostas chegarem aos usuários.
5. **Carga e resiliência**: tuning de connection pool já existe; adicione uma fila/back-pressure para chamadas de LLM e circuit breakers (tenacity já é dependência).

Resumo: **não reconstrua o harness; escolha uma vertical de A a C, entregue o resultado e use evals + tracing integrados como prova de qualidade e argumento de venda.**
