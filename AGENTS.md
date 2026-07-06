# Guia de Desenvolvimento de Agentes de IA

Este documento traz diretrizes essenciais para agentes de IA que trabalham neste projeto LangGraph + FastAPI.

## Visão Geral do Projeto

Esta é uma aplicação de agentes de IA pronta para produção, construída com:

- **LangGraph** para workflows de agentes com estado e múltiplas etapas
- **FastAPI** para endpoints REST assíncronos de alta performance
- **Langfuse** para observabilidade e tracing de LLM
- **PostgreSQL + pgvector** para armazenamento de memória de longo prazo (mem0ai)
- **Autenticação JWT** com gerenciamento de sessões
- **Prometheus + Grafana** para monitoramento

## Referência Rápida: Regras Críticas

### Regras de Import

- **Todos os imports DEVEM ficar no topo do arquivo**. Nunca adicione imports dentro de funções ou classes.

### Regras de Logging

- Use **structlog** para todos os logs.
- Mensagens de log devem estar em **lowercase_with_underscores** (ex.: `"user_login_successful"`).
- **NÃO use f-strings em eventos do structlog**. Passe variáveis como kwargs.
- Use `logger.exception()` em vez de `logger.error()` para preservar tracebacks.
- Exemplo: `logger.info("chat_request_received", session_id=session.id, message_count=len(messages))`

### Regras de Cache

- **Faça cache apenas de respostas bem-sucedidas**, nunca de erros.
- Use TTL adequado conforme a volatilidade dos dados.

### Regras FastAPI

- Todas as rotas devem ter decorators de rate limiting.
- Use dependency injection para serviços, conexões de banco e autenticação.
- Todas as operações de banco devem ser assíncronas.

## Convenções de Estilo de Código

### Python/FastAPI

- Use `async def` para operações assíncronas.
- Use type hints em todas as assinaturas de função.
- Prefira modelos Pydantic a dicionários crus.
- Use programação funcional e declarativa; evite classes exceto para serviços e agentes.
- Nome de arquivo: minúsculo com underscores (ex.: `user_routes.py`).
- Use o padrão RORO (Receive an Object, Return an Object).

### Tratamento de Erros

- Trate erros no início das funções.
- Use retornos antecipados para condições de erro.
- Deixe o caminho feliz por último na função.
- Use guard clauses para pré-condições.
- Use `HTTPException` para erros esperados com status codes adequados.

## Padrões LangGraph e LangChain

### Estrutura de Grafo

- Use `StateGraph` para construir workflows de agentes de IA.
- Defina schemas de estado claros usando modelos Pydantic.
- Use `CompiledStateGraph` para workflows em produção.
- Implemente `AsyncPostgresSaver` para checkpointing e persistência.
- Use `Command` para controlar o fluxo do grafo entre nós.

## Operações de Banco de Dados

- Use SQLModel para modelos ORM (combina SQLAlchemy + Pydantic).
- Use operações assíncronas de banco com asyncpg.
- Use `AsyncPostgresSaver` do LangGraph para checkpointing de agentes.

## Diretrizes de Performance

- Minimize operações de I/O bloqueantes.
- Use async para todas as chamadas de banco e APIs externas.
- Implemente cache para dados acessados com frequência.
- Use connection pooling para conexões de banco.
- Otimize chamadas de LLM com respostas em streaming.

## Observabilidade

- Integre Langfuse para tracing de LLM em todas as operações dos agentes.
- Exporte métricas Prometheus para performance da API.
- Use logging estruturado com context binding (`request_id`, `session_id`, `user_id`).
- Acompanhe duração de inferência da LLM, uso de tokens e custos.

## Testes e Avaliação

- Implemente avaliações baseadas em métricas para saídas de LLM (veja o diretório `src/evals/`).
- Crie métricas customizadas como arquivos markdown em `src/evals/metrics/prompts/`.
- Use traces do Langfuse como fontes de dados para avaliação.
- Gere relatórios JSON com taxas de sucesso.

## Gerenciamento de Configuração

- Use arquivos de configuração por ambiente (`.env.development`, `.env.staging`, `.env.production`).
- Use Pydantic Settings para configuração tipada (veja `app/core/config.py`).
- Nunca deixe secrets ou chaves de API hardcoded.

## Dependências Principais

- **FastAPI**: framework web
- **LangGraph**: orquestração de workflows de agentes
- **LangChain**: abstração de LLM e ferramentas
- **Langfuse**: observabilidade e tracing de LLM
- **Pydantic v2**: validação de dados e settings
- **structlog**: logging estruturado
- **mem0ai**: gerenciamento de memória de longo prazo
- **PostgreSQL + pgvector**: banco de dados e armazenamento vetorial
- **SQLModel**: ORM para modelos de banco
- **tenacity**: lógica de retry
- **rich**: formatação de terminal
- **slowapi**: rate limiting
- **prometheus-client**: coleta de métricas

## 10 Mandamentos Deste Projeto

1. Todas as rotas devem ter decorators de rate limiting.
2. Todas as operações de LLM devem ter tracing Langfuse.
3. Todas as operações assíncronas devem ter tratamento de erro adequado.
4. Todos os logs devem seguir logging estruturado com nomes de evento em `lowercase_underscore`.
5. Todos os retries devem usar a biblioteca tenacity.
6. Todas as saídas de console devem usar formatação rich.
7. Todo cache deve armazenar apenas respostas bem-sucedidas.
8. Todos os imports devem ficar no topo dos arquivos.
9. Todas as operações de banco devem ser assíncronas.
10. Todos os endpoints devem ter type hints e modelos Pydantic adequados.

## Armadilhas Comuns a Evitar

- Usar f-strings em eventos do `structlog`.
- Adicionar imports dentro de funções.
- Esquecer decorators de rate limiting em rotas.
- Deixar chamadas de LLM sem tracing Langfuse.
- Fazer cache de respostas de erro.
- Usar `logger.error()` em vez de `logger.exception()` para exceções.
- Fazer I/O bloqueante sem async.
- Deixar secrets ou chaves de API hardcoded.
- Omitir type hints em assinaturas de função.

## Ao Fazer Alterações

Antes de modificar código:

1. Leia primeiro a implementação existente.
2. Verifique padrões relacionados no codebase.
3. Garanta consistência com o estilo de código existente.
4. Adicione logging adequado em formato estruturado.
5. Inclua tratamento de erros com retornos antecipados.
6. Adicione type hints e modelos Pydantic.
7. Verifique se o tracing Langfuse está habilitado para chamadas de LLM.

## Referências

- Documentação LangGraph: https://langchain-ai.github.io/langgraph/
- Documentação LangChain: https://python.langchain.com/docs/
- Documentação FastAPI: https://fastapi.tiangolo.com/
- Documentação Langfuse: https://langfuse.com/docs

# Plano de Execução de Tarefas

Importante: sempre planeje a tarefa passo a passo antes de escrever código. Peça permissão para prosseguir com o plano.

Importante: antes de prosseguir com o plano, crie um novo arquivo chamado `.codex/plans/name-of-the-task.md`. Com base no plano aprovado, liste todas as etapas necessárias de implementação como checkboxes no estilo GitHub (`- [ ] Descrição da etapa`). Use subitens para detalhes granulares dentro de cada etapa principal.

- Os planos devem ser detalhados o suficiente para execução sem ambiguidade.
- Cada tarefa do plano deve incluir ao menos um teste de validação para confirmar que funciona.
- Avalie a complexidade e a viabilidade em uma única passada: um agente consegue realisticamente concluir isso de uma vez?
- Inclua um indicador de complexidade no topo de cada plano:
  - Simples: executável em uma passada, baixo risco.
  - Médio: pode exigir iteração, alguma complexidade.
  - Complexo: divida em subplanos antes de executar.

**CRÍTICO: depois de concluir cada etapa com sucesso, você DEVE atualizar o arquivo `.codex/plans/name-of-the-task.md`, alterando o checkbox correspondente de `- [ ]` para `- [x]`.**

Prossiga apenas para o *próximo* item não marcado depois de confirmar que o anterior foi marcado no arquivo. Anuncie qual etapa está começando.
