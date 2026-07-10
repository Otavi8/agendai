# Deploy do AgendAI na VPS com GitHub Actions

Este fluxo publica a imagem da API no GitHub Container Registry e atualiza a VPS via SSH usando Docker Compose.

## Pré-requisitos na VPS

- Docker e Docker Compose funcionando.
- Repositório clonado na VPS, por exemplo em `/opt/agendai`.
- Arquivo `.env.production` criado na raiz do projeto na VPS.

Exemplo de preparação inicial na VPS:

```bash
sudo mkdir -p /opt/agendai
sudo chown -R "$USER":"$USER" /opt/agendai
cd /opt/agendai
git clone URL_DO_REPOSITORIO .
cp .env.example .env.production
nano .env.production
```

No `.env.production`, ajuste pelo menos:

```bash
APP_ENV=production
PROJECT_NAME=AgendAI
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=agendai
POSTGRES_USER=agendai
POSTGRES_PASSWORD=troque-esta-senha
JWT_SECRET_KEY=troque-esta-chave
OPENAI_API_KEY=sua-chave-openai
MCP_ENABLED=false
AGENDAI_ENABLE_REAL_EMAIL=false
AGENDAI_ENABLE_REAL_WHATSAPP=false
AGENDAI_ENABLE_REAL_MINIO=false
APP_PORT=8000
```

## Secrets no GitHub

Cadastre estes secrets em:

`Settings -> Secrets and variables -> Actions -> New repository secret`

| Secret | Exemplo | Uso |
|--------|---------|-----|
| `VPS_HOST` | `123.123.123.123` | IP ou host da VPS. |
| `VPS_USER` | `root` ou `deploy` | Usuario SSH usado no deploy. |
| `VPS_SSH_KEY` | chave privada SSH | Chave privada autorizada na VPS. |
| `VPS_SSH_PORT` | `22` | Porta SSH. Opcional se for 22. |
| `VPS_DEPLOY_PATH` | `/opt/agendai` | Pasta onde o repo fica na VPS. |

O workflow usa `GITHUB_TOKEN` automaticamente para publicar e puxar a imagem em `ghcr.io`.

## Fluxo do GitHub Actions

Em push na branch `main`, o workflow:

1. Instala Python e `uv`.
2. Roda `uv sync --group test`.
3. Roda `uv run pytest tests/integration -q`.
4. Builda a imagem Docker.
5. Publica em `ghcr.io/<owner>/<repo>:latest`.
6. Conecta na VPS por SSH.
7. Executa:

```bash
cd /opt/agendai
docker compose pull app
docker compose up -d db app prometheus grafana cadvisor
docker compose exec -T app python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health').read().decode())"
```

## Primeiro deploy manual opcional

Antes de confiar no Actions, voce pode validar na VPS:

```bash
cd /opt/agendai
export APP_ENV=production
export APP_IMAGE=agendai-app:local
docker compose up -d --build db app
docker compose ps
docker compose logs -f app
```

Health check:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

Swagger:

```text
http://IP_DA_VPS:8000/docs
```

## Observações

- O arquivo `.env.production` fica somente na VPS e nunca deve ser commitado.
- Gmail, WhatsApp e MinIO continuam desabilitados por padrão neste MVP.
- Para domínio/HTTPS depois, adicione um proxy reverso como Nginx, Caddy ou Traefik.
