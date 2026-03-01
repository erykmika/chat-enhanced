import asyncio
import contextlib
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

import jwt
import redis.asyncio as redis
from websockets.exceptions import ConnectionClosed
from websockets.server import WebSocketServerProtocol, serve

logger = logging.getLogger(__name__)

MESSAGE_CHANNEL = "chat:messages"
PRESENCE_CHANNEL = "chat:presence"
ONLINE_SET = "chat:online_users"
ONLINE_COUNT_PREFIX = "chat:online_count:"


@dataclass
class ConnectedClient:
    email: str
    socket: WebSocketServerProtocol


class ChatHub:
    def __init__(
        self,
        jwt_secret: str,
        redis_url: str | None = None,
        redis_required: bool = False,
        redis_retries: int = 5,
        redis_delay: float = 1.0,
    ) -> None:
        self._jwt_secret = jwt_secret
        self._redis_url = redis_url
        self._redis_required = redis_required
        self._redis_retries = max(redis_retries, 1)
        self._redis_delay = max(redis_delay, 0.1)
        self._clients: dict[str, WebSocketServerProtocol] = {}
        self._lock = asyncio.Lock()
        self._redis: redis.Redis | None = None
        self._pubsub: redis.client.PubSub | None = None
        self._pubsub_task: asyncio.Task[None] | None = None
        self._server_id = uuid4().hex

    async def start(self) -> None:
        if not self._redis_url:
            return

        for attempt in range(1, self._redis_retries + 1):
            try:
                self._redis = redis.from_url(
                    self._redis_url, decode_responses=True
                )
                await self._redis.ping()
                self._pubsub = self._redis.pubsub()
                await self._pubsub.subscribe(MESSAGE_CHANNEL, PRESENCE_CHANNEL)
                self._pubsub_task = asyncio.create_task(self._redis_listener())
                return
            except Exception as exc:
                logger.warning(
                    "Redis unavailable (attempt %s/%s): %s",
                    attempt,
                    self._redis_retries,
                    exc,
                )
                if self._redis:
                    await self._redis.close()
                    self._redis = None
                await asyncio.sleep(self._redis_delay)

        if self._redis_required:
            raise RuntimeError("Redis is required but unavailable")

    async def stop(self) -> None:
        if self._pubsub_task:
            self._pubsub_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._pubsub_task

        if self._pubsub:
            await self._pubsub.close()

        if self._redis:
            await self._redis.close()

    async def handler(
        self, websocket: WebSocketServerProtocol, path: str
    ) -> None:
        email = await self._authenticate(websocket, path)
        if not email:
            return

        await self._register(email, websocket)
        await self._send_user_list(websocket)

        try:
            async for raw_message in websocket:
                await self._handle_message(email, websocket, raw_message)
        except ConnectionClosed:
            logger.info(f"Connection closed for {email}")
        finally:
            await self._unregister(email, websocket)

    async def _authenticate(
        self, websocket: WebSocketServerProtocol, path: str
    ) -> str | None:
        token = self._token_from_path(path)
        if not token:
            token = await self._token_from_auth_message(websocket)

        if not token:
            await self._safe_send(
                websocket,
                {"type": "error", "message": "Missing auth token."},
            )
            await websocket.close(code=4001, reason="Missing auth token")
            return None

        try:
            payload = jwt.decode(token, self._jwt_secret, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            await self._safe_send(
                websocket,
                {"type": "error", "message": "Invalid auth token."},
            )
            await websocket.close(code=4002, reason="Invalid auth token")
            return None

        email = payload.get("email")
        if not isinstance(email, str) or not email:
            await self._safe_send(
                websocket,
                {"type": "error", "message": "Invalid auth payload."},
            )
            await websocket.close(code=4003, reason="Invalid auth payload")
            return None

        return email

    def _token_from_path(self, path: str) -> str | None:
        query = urlparse(path).query
        params = parse_qs(query)
        return params.get("token", [None])[0]

    async def _token_from_auth_message(
        self, websocket: WebSocketServerProtocol
    ) -> str | None:
        try:
            raw = await asyncio.wait_for(websocket.recv(), timeout=5)
        except asyncio.TimeoutError:
            return None

        try:
            message = json.loads(raw)
        except json.JSONDecodeError:
            return None

        if not isinstance(message, dict):
            return None

        if message.get("type") != "auth":
            return None

        token = message.get("token")
        return token if isinstance(token, str) else None

    async def _register(
        self, email: str, websocket: WebSocketServerProtocol
    ) -> None:
        async with self._lock:
            existing = self._clients.get(email)
            if existing and existing is not websocket:
                await existing.close(code=4000, reason="New connection")
            self._clients[email] = websocket

        if self._redis:
            state_changed = await self._mark_online(email)
            if state_changed:
                await self._broadcast_user_status(email, True)
        else:
            await self._broadcast_user_status(email, True)

    async def _unregister(
        self, email: str, websocket: WebSocketServerProtocol
    ) -> None:
        async with self._lock:
            is_current = self._clients.get(email) is websocket
            if is_current:
                self._clients.pop(email, None)

        if self._redis:
            state_changed = await self._mark_offline(email)
            if state_changed:
                await self._broadcast_user_status(email, False)
        elif is_current:
            await self._broadcast_user_status(email, False)

    async def _handle_message(
        self, email: str, websocket: WebSocketServerProtocol, raw: str
    ) -> None:
        try:
            message = json.loads(raw)
        except json.JSONDecodeError:
            await self._safe_send(
                websocket,
                {"type": "error", "message": "Invalid JSON payload."},
            )
            return

        if not isinstance(message, dict):
            await self._safe_send(
                websocket,
                {"type": "error", "message": "Invalid message payload."},
            )
            return

        message_type = message.get("type")
        if message_type == "message":
            await self._handle_chat_message(email, websocket, message)
        elif message_type == "list_users":
            await self._send_user_list(websocket)
        else:
            await self._safe_send(
                websocket,
                {"type": "error", "message": "Unsupported message type."},
            )

    async def _handle_chat_message(
        self,
        email: str,
        websocket: WebSocketServerProtocol,
        message: dict[str, Any],
    ) -> None:
        recipient = message.get("to")
        content = message.get("content")

        if not isinstance(recipient, str) or not recipient:
            await self._safe_send(
                websocket,
                {"type": "error", "message": "Missing recipient."},
            )
            return

        if not isinstance(content, str) or not content.strip():
            await self._safe_send(
                websocket,
                {"type": "error", "message": "Message cannot be empty."},
            )
            return

        payload = {
            "type": "message",
            "from": email,
            "to": recipient,
            "content": content.strip(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        await self._publish_message(payload)

    async def _send_to(self, email: str, payload: dict[str, Any]) -> None:
        async with self._lock:
            recipient = self._clients.get(email)

        if recipient:
            await self._safe_send(recipient, payload)

    async def _send_user_list(
        self, websocket: WebSocketServerProtocol
    ) -> None:
        if self._redis:
            users = list(await self._redis.smembers(ONLINE_SET))
        else:
            async with self._lock:
                users = list(self._clients.keys())

        payload = {
            "type": "user_list",
            "users": [{"email": user, "online": True} for user in users],
        }
        await self._safe_send(websocket, payload)

    async def _broadcast_user_status(self, email: str, online: bool) -> None:
        await self._broadcast_user_status_local(email, online)
        await self._publish_presence(email, online)

    async def _broadcast_user_status_local(
        self, email: str, online: bool
    ) -> None:
        async with self._lock:
            sockets = list(self._clients.values())

        payload = {"type": "user_status", "email": email, "online": online}
        await asyncio.gather(
            *(self._safe_send(socket, payload) for socket in sockets),
            return_exceptions=True,
        )

    async def _publish_message(self, payload: dict[str, Any]) -> None:
        if not self._redis:
            await self._deliver_message(payload)
            return

        message = {"event": "message", "payload": payload}
        try:
            await self._redis.publish(MESSAGE_CHANNEL, json.dumps(message))
        except Exception:
            logger.exception("Failed to publish message, delivering locally.")
            await self._deliver_message(payload)

    async def _publish_presence(self, email: str, online: bool) -> None:
        if not self._redis:
            return

        message = {
            "event": "presence",
            "origin": self._server_id,
            "payload": {"email": email, "online": online},
        }
        await self._redis.publish(PRESENCE_CHANNEL, json.dumps(message))

    async def _deliver_message(self, payload: dict[str, Any]) -> None:
        recipient = payload.get("to")
        if not isinstance(recipient, str) or not recipient:
            return
        await self._send_to(recipient, payload)

    async def _mark_online(self, email: str) -> bool:
        if not self._redis:
            return True

        count_key = f"{ONLINE_COUNT_PREFIX}{email}"
        count = await self._redis.incr(count_key)
        if count == 1:
            await self._redis.sadd(ONLINE_SET, email)
            return True
        return False

    async def _mark_offline(self, email: str) -> bool:
        if not self._redis:
            return True

        count_key = f"{ONLINE_COUNT_PREFIX}{email}"
        count = await self._redis.decr(count_key)
        if count <= 0:
            await self._redis.delete(count_key)
            await self._redis.srem(ONLINE_SET, email)
            return True
        return False

    async def _redis_listener(self) -> None:
        if not self._pubsub:
            return

        try:
            async for raw in self._pubsub.listen():
                if raw.get("type") != "message":
                    continue

                data = raw.get("data")
                if isinstance(data, bytes):
                    data = data.decode("utf-8")

                try:
                    message = json.loads(data)
                except json.JSONDecodeError:
                    continue

                event = message.get("event")
                if event == "message":
                    payload = message.get("payload")
                    if isinstance(payload, dict):
                        await self._deliver_message(payload)
                elif event == "presence":
                    if message.get("origin") == self._server_id:
                        continue
                    payload = message.get("payload")
                    if not isinstance(payload, dict):
                        continue
                    email = payload.get("email")
                    online = payload.get("online")
                    if isinstance(email, str) and isinstance(online, bool):
                        await self._broadcast_user_status_local(email, online)
        except asyncio.CancelledError:
            return
        except Exception:
            logger.exception("Redis listener failed")

    async def _safe_send(
        self, websocket: WebSocketServerProtocol, payload: dict[str, Any]
    ) -> None:
        try:
            await websocket.send(json.dumps(payload))
        except ConnectionClosed:
            return


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    host = os.getenv("WS_HOST", "0.0.0.0")
    port = int(os.getenv("WS_PORT", "8001"))
    jwt_secret = os.getenv("JWT_SECRET", "123somerandomjwtsecret123")
    redis_url = os.getenv("REDIS_URL")
    redis_required = os.getenv("REDIS_REQUIRED", "0").lower() in {
        "1",
        "true",
        "yes",
    }
    redis_retries = int(os.getenv("REDIS_CONNECT_RETRIES", "10"))
    redis_delay = float(os.getenv("REDIS_CONNECT_DELAY", "1"))

    chat_hub = ChatHub(
        jwt_secret,
        redis_url,
        redis_required=redis_required,
        redis_retries=redis_retries,
        redis_delay=redis_delay,
    )
    await chat_hub.start()

    logger.info(f"Starting ws server on {host}:{port}")
    try:
        async with serve(chat_hub.handler, host, port, max_size=2**20):
            await asyncio.Future()
    finally:
        await chat_hub.stop()


if __name__ == "__main__":
    asyncio.run(main())
