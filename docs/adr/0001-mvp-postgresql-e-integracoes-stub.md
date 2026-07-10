# ADR 0001: MVP com PostgreSQL Docker e Integrações Externas em Stub

Status: Aceito

Data: 2026-07-09

## Contexto

O AgendAI precisa apoiar a gestão de pátio, incluindo cadastro de motoristas, agendamentos, check-ins por QR Code, alertas de atraso, consultas históricas e apoio analítico por agente de IA.

O produto também prevê integrações com Gmail, WhatsApp e MinIO. Essas integrações envolvem credenciais, serviços externos, automações reais e riscos de envio indevido de mensagens ou exposição de dados sensíveis.

## Decisão

A primeira versão será construída sobre o PostgreSQL Docker já previsto pelo harness.

No MVP, o foco será:

- Modelar e persistir os dados centrais do domínio AgendAI.
- Criar APIs autenticadas para operar motoristas, veículos, fornecedores, agendamentos, check-ins e alertas.
- Criar uma tela operacional simples para a equipe de recebimento.
- Criar/adaptar o agente AgendAI para consultar e explicar os dados do domínio.

Gmail, WhatsApp e MinIO serão tratados inicialmente como interfaces ou stubs seguros, sem envio real de e-mails, mensagens ou ingestão real de documentos por padrão.

## Consequências

### Positivas

- Reduz o risco de acoplamento prematuro com serviços externos.
- Permite validar o fluxo principal de negócio antes de configurar credenciais reais.
- Evita envio acidental de e-mails ou mensagens durante desenvolvimento.
- Mantém o projeto alinhado ao harness existente, reaproveitando autenticação, sessões, banco, guardrails e frontend.

### Negativas

- O MVP não validará ainda a entrega real de e-mails, mensagens WhatsApp ou documentos MinIO.
- Será necessário implementar uma etapa posterior para trocar os stubs por adaptadores reais.

## Validação

- O `CONTEXT.md` registra PostgreSQL Docker como fonte principal do MVP.
- O plano `.codex/plans/planejamento-inicial-agendai.md` mantém integrações externas como interfaces/stubs na primeira fase.
- Nenhuma credencial real deve ser criada ou exigida para Gmail, WhatsApp ou MinIO nesta decisão.
