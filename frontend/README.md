# Agent Harness: Frontend (React + Vite + TS + Tailwind)

Uma UI de chat mínima, mas real, para o agente `chatbot` do harness: cadastro/login, criação automática de sessão e chat em streaming com histórico mantido no servidor.

## Pré-requisitos

- Node 18+ (testado no Node 24)
- **Backend rodando** em `http://localhost:8000` (`.\dev.ps1` na raiz do repositório)

## Rodar

```bash
cd frontend
npm install        # apenas na primeira vez
npm run dev        # serve em http://localhost:5173
```

Abra **http://localhost:5173**. O dev server do Vite faz proxy de toda chamada `/api/*` para o backend em `:8000` (veja `vite.config.ts`), então não há problemas de CORS nem tokens em URLs.

> Nota de porta: a UI roda na **5173** (padrão do Vite) porque a porta 3000 costuma estar ocupada por outros apps locais. Altere `server.port` em `vite.config.ts` se necessário.

## Como Funciona

- **Dois tokens.** Cadastro/login retorna um *token de usuário*; o app chama imediatamente `POST /auth/session` para obter um *token de sessão*. Os endpoints de chat exigem o token de sessão. Ambos ficam em `localStorage` (`agent_harness_auth`).
- **Streaming.** `POST /chatbot/chat/stream` retorna Server-Sent Events; `src/lib/api.ts` faz o parsing com `fetch` + leitor `ReadableStream` e entrega tokens conforme chegam.
- **Histórico vive no servidor.** O LangGraph faz checkpoints por sessão, então a UI envia apenas a nova mensagem do usuário a cada turno e carrega turnos anteriores via `GET /chatbot/messages`.

## Estrutura

```text
src/
  main.tsx              # entrypoint, envolve <App> em <AuthProvider>
  App.tsx               # alterna entre LoginScreen e ChatScreen
  context/AuthContext.tsx  # tokens, register/login/logout, criação de sessão
  lib/api.ts            # cliente de API tipado + streaming SSE
  lib/types.ts          # tipos TS espelhando os DTOs do backend
  components/
    LoginScreen.tsx     # formulário de cadastro / login
    ChatScreen.tsx      # lista de mensagens + enviar + limpar + nova sessão
    MessageBubble.tsx   # uma mensagem (indicador digitando durante streaming)
    Composer.tsx        # caixa de input (Enter envia, Shift+Enter quebra linha)
```

## Build

```bash
npm run build     # type-check (tsc -b) e bundle para dist/
npm run preview   # serve o build de produção localmente
```

## Próximas Ideias

- Sidebar de sessões (listar via `GET /auth/sessions`, alternar/renomear/excluir).
- Abas para os outros agentes (`/text-to-sql`, `/deep-research`).
- Tratamento de expiração de token + refresh e renderização markdown das respostas do assistente.
