# WebSocket Server (MVP)

Minimal websocket server for peer-to-peer chat.

## Run

Set the JWT secret to match the Flask backend and start the server.

```bash
set JWT_SECRET=dev-jwt-secret-change-me
python -m backend.ws_server.server
```

### Redis fan-out (multi-process)

Set `REDIS_URL` to enable cross-process message fan-out and shared presence.

```bash
set JWT_SECRET=dev-jwt-secret-change-me
set REDIS_URL=redis://localhost:6379/0
python -m backend.ws_server.server
```

You can run multiple processes (or containers) pointing at the same Redis.

Optional settings:
- `REDIS_REQUIRED=1` to fail fast when Redis is unavailable.
- `REDIS_CONNECT_RETRIES` and `REDIS_CONNECT_DELAY` to tune startup retry behavior.

## Protocol

- Client connects to `ws://host:port?token=<jwt>` or sends `{ "type": "auth", "token": "..." }` as the first message.
- Send chat messages with `{ "type": "message", "to": "user@example.com", "content": "Hello" }`.
- Server delivers `{ "type": "message", "from": "user@example.com", "content": "Hello", "timestamp": "..." }`.
- Request online users with `{ "type": "list_users" }`.
