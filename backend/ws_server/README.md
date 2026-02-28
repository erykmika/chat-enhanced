# WebSocket Server (MVP)

Minimal websocket server for peer-to-peer chat.

## Run

Set the JWT secret to match the Flask backend and start the server.

```bash
set JWT_SECRET=dev-jwt-secret-change-me
python -m backend.ws_server.server
```

## Protocol

- Client connects to `ws://host:port?token=<jwt>` or sends `{ "type": "auth", "token": "..." }` as the first message.
- Send chat messages with `{ "type": "message", "to": "user@example.com", "content": "Hello" }`.
- Server delivers `{ "type": "message", "from": "user@example.com", "content": "Hello", "timestamp": "..." }`.
- Request online users with `{ "type": "list_users" }`.

