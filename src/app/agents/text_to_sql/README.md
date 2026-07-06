# Deep Agent Text-to-SQL

Um agente de consulta SQL a partir de linguagem natural, movido pelo framework **Deep Agents** do LangChain. Esta é uma versão avançada de um agente text-to-SQL com capacidades de planejamento, filesystem e subagentes.

## O Que é Deep Agents?

Deep Agents é um framework sofisticado de agentes construído sobre LangGraph que fornece:

- **Capacidades de planejamento**: divide tarefas complexas com a ferramenta `write_todos`.
- **Backend de filesystem**: salva e recupera contexto com operações de arquivo.
- **Criação de subagentes**: delega tarefas especializadas para agentes focados.
- **Gerenciamento de contexto**: evita estouro da janela de contexto em tarefas complexas.

## Banco de Demonstração

Usa o [banco Chinook](https://github.com/lerocha/chinook-database), um banco de exemplo que representa uma loja de mídia digital.

## Início Rápido

### Instalação

1. Baixe o banco Chinook:

```bash
# Baixa o arquivo SQLite
curl -L -o chinook.db https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite
```

### Configuração

Deep Agents usa **divulgação progressiva** com arquivos de memória e skills:

**AGENTS.md** (sempre carregado) contém:

- Identidade e papel do agente.
- Princípios centrais e regras de segurança.
- Diretrizes gerais.
- Estilo de comunicação.

**skills/** (carregado sob demanda) contém workflows especializados:

- **query-writing**: como escrever e executar consultas SQL simples e complexas.
- **schema-exploration**: como descobrir a estrutura e os relacionamentos do banco.

O agente vê as descrições das skills no contexto, mas só carrega as instruções completas do `SKILL.md` quando determina qual skill é necessária para a tarefa atual. Esse padrão de **divulgação progressiva** mantém o contexto eficiente e oferece profundidade quando necessário.

## Exemplos de Consultas

### Consulta Simples

```text
"How many customers are from Canada?"
```

O agente consulta diretamente e retorna a contagem.

### Consulta Complexa com Planejamento

```text
"Which employee generated the most revenue and from which countries?"
```

O agente irá:

1. Usar `write_todos` para planejar a abordagem.
2. Identificar tabelas necessárias (`Employee`, `Invoice`, `Customer`).
3. Planejar a estrutura de `JOIN`.
4. Executar a consulta.
5. Formatar os resultados com análise.

## Exemplo de Saída do Agente Text-to-SQL

O Deep Agent mostra seu processo de raciocínio:

```text
Question: Which employee generated the most revenue by country?

[Planning Step]
Using write_todos:
- [ ] List tables in database
- [ ] Examine Employee and Invoice schemas
- [ ] Plan multi-table JOIN query
- [ ] Execute and aggregate by employee and country
- [ ] Format results

[Execution Steps]
1. Listing tables...
2. Getting schema for: Employee, Invoice, InvoiceLine, Customer
3. Generating SQL query...
4. Executing query...
5. Formatting results...

[Final Answer]
Employee Jane Peacock (ID: 3) generated the most revenue...
Top countries: USA ($1000), Canada ($500)...
```
