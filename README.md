# Real-time chat web app

### Development setup

```
uv venv
uv pip install pre-commit
pre-commit install

# Install backend deps from pyproject.toml
pip install -e ".[dev]"
```

## Docker (frontend + backend + Postgres)

Environment files:
- `backend/.env` (optional; for running the backend locally outside Docker)
- `backend/.env.example` (template)
- `.env` at repo root (optional; used by Docker Compose automatically to override db credentials)
- `.env.example` at repo root (template)

Dockerfile locations:
- Backend webapp: `backend/webapp/Dockerfile` (entrypoint: `backend/webapp/docker-entrypoint.sh`)
- WebSocket server: `backend/ws_server/Dockerfile`
- Frontend: `frontend/Dockerfile`

The compose stack includes:
- Postgres (database)
- MailHog (SMTP sink + UI)
- Flask backend
- WebSocket server (Redis-backed fan-out)
- WebSocket load balancer (nginx)
- Redis (message bus for websockets)
- Vite/React frontend (served by nginx)

Run the full stack:

```bash
# Optional: override POSTGRES_* used by the db container
cp .env.example .env

docker compose build
docker compose up
```

Notes:
- The compose stack does not load `backend/.env`. Backend config is set inline in `docker-compose.yml`.
- If you run compose without setting `POSTGRES_PASSWORD`, Postgres will refuse to start. This repo provides dev defaults.
- To run multiple websocket processes, scale `ws_server` and keep clients pointed at `ws_lb`:

```bash
docker compose up --scale ws_server=3
```

Open:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000 (health: `/health`)
- WebSocket (via load balancer): ws://localhost:8011
- MailHog UI: http://localhost:8025 (SMTP: localhost:1025)

Stop and remove containers (and the db volume):

```bash
docker compose down -v
```

### Running alembic

```
alembic check
alembic upgrade head
```

#### Creating a new migration
```
alembic revision --autogenerate -m "<msg>"
```