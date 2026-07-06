# Perguntas para Descoberta do Projeto

Este roteiro adapta a ideia do `grill-with-docs`: fazer perguntas uma de cada vez, resolver o vocabulário do projeto e registrar o contexto conforme ele amadurece.

Como usar:

1. Responda uma pergunta por vez, do jeito que souber.
2. Se não souber, responda "não sei ainda".
3. Depois de cada bloco de respostas, o `CONTEXT.md` deve ser atualizado.
4. Decisões difíceis de reverter devem virar ADR em `docs/adr/`.

## Bloco 1: Problema e Valor

1. Qual problema real você quer resolver com este agente?
2. Quem sente esse problema hoje?
3. Como esse problema é resolvido atualmente?
4. O que fica caro, lento, manual ou arriscado no processo atual?
5. O que precisaria acontecer para você dizer: "esse agente valeu a pena"?

## Bloco 2: Usuários e Contexto

6. Quem será o primeiro tipo de usuário do sistema?
7. Esse usuário é interno da empresa, cliente externo ou ambos?
8. Ele vai usar o agente todos os dias, de vez em quando ou só em situações específicas?
9. Qual é o nível técnico desse usuário?
10. Onde esse usuário provavelmente vai interagir com o agente: frontend web, WhatsApp, API, CLI, outro canal?

## Bloco 3: Primeira Versão Pequena

11. Qual seria a menor versão útil desse agente?
12. Qual tarefa única ele precisa fazer muito bem na primeira versão?
13. O que pode ficar fora da primeira versão sem prejudicar o teste inicial?
14. Existe alguma tela, relatório, conversa ou processo atual que podemos usar como referência?
15. Qual seria um exemplo real de pergunta que o usuário faria ao agente?

## Bloco 4: Dados e Integrações

16. De onde virão as informações que o agente precisa consultar?
17. Essas informações estão em banco, planilha, API, PDF, site, pasta local ou outro lugar?
18. Existe alguma credencial, token ou acesso que precisará ser configurado depois?
19. Os dados mudam com que frequência?
20. O agente pode responder apenas com base nos dados disponíveis ou pode inferir quando faltar informação?

## Bloco 5: Ações do Agente

21. O agente apenas responde perguntas ou também deve executar ações?
22. Se ele executar ações, quais são permitidas?
23. Quais ações exigem confirmação humana antes de acontecer?
24. O agente pode criar, editar ou excluir dados?
25. O agente deve gerar algum artefato, como e-mail, PDF, relatório, planilha ou chamado?

## Bloco 6: Regras de Negócio

26. Quais regras o agente nunca pode violar?
27. Existem exceções importantes nessas regras?
28. O agente deve priorizar alguma categoria, cliente, loja, área ou tipo de solicitação?
29. Há termos do negócio que precisam ter definição exata?
30. Existem respostas que precisam seguir um padrão comercial, técnico ou jurídico?

## Bloco 7: Segurança, Privacidade e Guardrails

31. Que dados são sensíveis neste projeto?
32. O agente pode mostrar dados pessoais?
33. O agente pode mostrar informações financeiras, comerciais ou estratégicas?
34. O que o agente deve fazer quando o usuário pedir algo fora do escopo?
35. O que o agente deve fazer quando não encontrar resposta nos dados?

## Bloco 8: Memória e Personalização

36. O agente deve lembrar preferências do usuário entre conversas?
37. Que tipo de informação vale a pena guardar na memória de longo prazo?
38. Que tipo de informação nunca deve ser guardada?
39. A memória deve ser por usuário, por equipe, por cliente ou por sessão?
40. O usuário deve conseguir apagar ou corrigir algo que o agente lembra?

## Bloco 9: Experiência de Uso

41. A resposta ideal deve ser curta, detalhada, em tópicos, em tabela ou em formato de texto pronto para envio?
42. O agente deve citar fontes ou explicar de onde tirou a resposta?
43. O agente deve perguntar antes de continuar quando houver ambiguidade?
44. O tom deve ser formal, consultivo, técnico, comercial ou casual?
45. Quais seriam três exemplos de respostas excelentes?

## Bloco 10: Produto e Operação

46. Quem vai administrar usuários, permissões e sessões?
47. Será necessário dashboard de uso, custo ou qualidade?
48. Como você vai medir se o agente está respondendo bem?
49. Quais erros seriam críticos em produção?
50. Existe prazo, público piloto ou ambiente inicial para testar?

## Primeira Pergunta Recomendada

Comece por esta:

> Qual problema real você quer resolver com este agente, e quem sente esse problema hoje?
