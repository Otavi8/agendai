# Contexto do Projeto

Este arquivo guarda o entendimento compartilhado sobre o produto que será construído usando este harness de agentes de IA.

Ele deve ser atualizado conforme as respostas forem ficando claras. A ideia é manter aqui o vocabulário, as decisões e os limites do projeto em linguagem simples, antes de transformar tudo em PRD, issues ou código.



### Objetivo inicial

Preciso criar um agente de IA que ajude na gestão de pátio de empresas, realizando o cadastro dos motoristas que entrarem em contato e armazenando essas informações em um banco de dados.

O agente deverá enviar e-mails (Gmail) para os fornecedores confirmando o agendamento assim que ele for realizado. Para isso, será necessário utilizar um MCP. Os dados dos agendamentos deverão ser gravados em uma tabela do banco de dados.

Também preciso que o agente envie mensagens via WhatsApp para os motoristas 10 minutos antes do horário agendado, perguntando se eles já chegaram à empresa.

O processo de check-in será realizado por meio de um QR Code. Quando o motorista chegar à empresa, ele deverá realizar o check-in, e essas informações deverão ser enviadas para uma tabela de check-ins, que também deverá ser criada e ficará acessível ao agente.

O agente deverá monitorar continuamente os check-ins e, caso algum motorista ultrapasse 10 minutos de atraso, deverá gerar um alerta em tela para a equipe de recebimento, perguntando se deseja chamar o próximo motorista agendado para iniciar o recebimento.

Além disso, o agente deverá auxiliar a equipe de recebimento, permitindo consultas sobre agendamentos históricos, respondendo perguntas e realizando análises.

A aplicação deverá possuir uma tela simples contendo todos os agendamentos. Ao selecionar um agendamento, deverão ser exibidas todas as informações relacionadas ao recebimento.

Na parte superior dessa tela deverá existir um resumo geral contendo:

- Quantidade de agendamentos pendentes;
- Quantidade de agendamentos realizados;
- Quantidade de check-ins realizados;
- Quantidade de cargas atrasadas.

O sistema deverá possuir autenticação por login e controle de acesso por grupos de usuários, pois o agente não estará disponível para todos os usuários e nem todos poderão visualizar informações de cargas ou outros dados sensíveis.

Também preciso que, além do prompt do agente, a área de negócio e a equipe de recebimento possam enviar documentos contendo regras de negócio para um bucket MinIO (Docker). O agente deverá utilizar essas informações como contexto para responder às perguntas. Portanto, também será necessária uma instância do MinIO.

### Usuário principal

- Equipes de recebimento de empresas com alto volume de entregas.

### Problema principal

- Organizar os recebimentos e a gestão de pátio de empresas que possuem um grande volume de entregas, além de auxiliar a equipe de recebimento na realização de análises e geração de insights utilizando agentes de IA.

### Resultado esperado

- Construir um processo completo, organizado e estruturado para realizar toda a gestão de pátio, acompanhamento dos recebimentos e análises de dados utilizando agentes de IA.

### Escopo do MVP confirmado

Para a primeira versão, o projeto seguirá uma entrega incremental:

1. Criar a base de dados do domínio AgendAI no PostgreSQL Docker do próprio projeto.
2. Implementar o backend mínimo para motoristas, veículos, fornecedores, agendamentos, check-ins e alertas.
3. Criar uma tela operacional simples com resumo geral, lista de agendamentos e detalhe do recebimento.
4. Criar/adaptar o agente AgendAI para consultar os dados do domínio e apoiar a equipe de recebimento.
5. Preparar interfaces seguras para Gmail, WhatsApp e MinIO, mas sem envio real de e-mails, mensagens ou leitura real de bucket nesta primeira etapa.

As integrações externas entrarão inicialmente como stubs ou adaptadores inativos por padrão. O objetivo é validar o fluxo principal antes de acoplar credenciais, serviços externos e automações reais.

## Glossário do Domínio

Por enquanto este processo não possui um glossário definido.

## Pessoas e Papéis

| Papel | Quem é | O que precisa resolver |
|-------|--------|------------------------|
| Usuário final | Motoristas ou transportadoras | Precisam realizar o cadastro para que possam efetuar entregas e serem auxiliados pelo agente durante todo o processo. |
| Administrador | Equipe de Analytics | Responsável pela manutenção da ferramenta e pela administração da aplicação. |
| Operador interno | Equipe de Recebimento | Deve acompanhar os recebimentos pelo sistema AgendAI, consultar o agente para esclarecer dúvidas ou realizar análises e cadastrar motoristas quando necessário. |

## Fluxos Principais

### Fluxo 1: A definir

### 1. Cadastro de Motoristas

Precisamos realizar o cadastro dos motoristas.

O motorista deverá iniciar o processo entrando em contato com o agente via WhatsApp.

Ao selecionar a opção de cadastro, o agente deverá solicitar um endereço de e-mail válido. Em seguida, enviará um código aleatório de confirmação para esse e-mail.

Após receber o código, o motorista deverá informá-lo ao agente pelo WhatsApp.

Depois da validação, o agente deverá fazer uma sequência de perguntas para concluir o cadastro, incluindo:

- Nome do motorista;
- Placa do veículo;
- Modelo;
- Cor;
- Ano;
- CPF do motorista;
- Empresa;
- Observações adicionais.

### 2. Agente

O agente deverá monitorar e orquestrar todos os recebimentos, auxiliar no cadastro de motoristas e acompanhar os horários das entregas, verificando se o motorista já chegou à empresa (caso ele ainda não tenha realizado o check-in).

Também deverá auxiliar a equipe de recebimento com análises, respostas a dúvidas e geração de alertas sempre que necessário.

### 3. Aplicação

A aplicação deverá apresentar uma visão geral e detalhada de todos os recebimentos.

Também deverá possuir uma área para interação com o agente, permitindo consultas sobre informações de recebimento, além de disponibilizar uma tela específica para cadastro de motoristas.

## Fontes de Dados

| Fonte | Tipo | Onde fica | Observações |
|-------|------|-----------|-------------|
| Banco de dados PostgreSQL | Banco relacional | Docker | Fonte principal do MVP para motoristas, veículos, fornecedores, agendamentos, check-ins e alertas. |
| Gmail | Integração externa/MCP | A definir | Preparar interface, mas não enviar e-mails reais no MVP. |
| WhatsApp | Integração externa | A definir | Preparar interface, mas não enviar mensagens reais no MVP. |
| MinIO | Bucket Docker | Docker | Preparar contrato para documentos de regras de negócio, mas sem ingestão real no MVP inicial. |

## Capacidades do Agente

O agente deve conseguir:

- Responder perguntas relacionadas aos agendamentos;
- Realizar cadastros em tabelas do banco de dados;
- Preparar confirmações de agendamento por e-mail;
- Preparar mensagens de aviso para motoristas;
- Interpretar mensagens de áudio futuramente, após definição da integração de entrada.

O agente não deve conseguir:

- Responder perguntas fora do seu escopo;
- Enviar e-mails para destinatários não autorizados;
- Alterar informações das tabelas mediante solicitação de usuários externos.

## Regras de Negócio

- As regras de negócio serão disponibilizadas em documentos armazenados em um bucket MinIO (Docker), que servirão como base de conhecimento para o agente.

## Guardrails e Segurança

- Dados sensíveis não poderão ser expostos fora da ferramenta de agendamentos.
- O agente não deverá responder perguntas sobre agendamentos para motoristas ou fornecedores.
- Alterações em agendamentos, cadastros de motoristas e placas deverão exigir confirmação humana.
- Assuntos fora do escopo nunca deverão ser respondidos.
- Quando não souber responder, o agente deverá informar ao usuário que a informação não faz parte do seu escopo ou que são necessárias mais informações para fornecer uma resposta.

## Decisões Já Tomadas

Decisões difíceis de reverter devem ganhar um ADR em `docs/adr/`.

| Decisão | Motivo | ADR |
|---------|--------|-----|
| Utilizar este Agent Harness como base | Aproveitar autenticação, memória, sessões, guardrails, observabilidade e frontend já existentes. |
| MVP com PostgreSQL Docker e integrações externas em stub | Reduzir risco inicial e validar o fluxo principal antes de acoplar Gmail, WhatsApp e MinIO reais. | `docs/adr/0001-mvp-postgresql-e-integracoes-stub.md` |
