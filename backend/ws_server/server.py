import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, urlparse

import jwt
from websockets.exceptions import ConnectionClosed
from websockets.server import WebSocketServerProtocol, serve

from backend.webapp.auth.domain.service.jwt import JwtService

logger = logging.getLogger(__name__)


@dataclass
class ConnectedClient:
    email: str
    socket: WebSocketServerProtocol


class ChatHub:
    def __init__(self, jwt_service: JwtService) -> None:
        self._jwt_service = jwt_service
        self._clients: dict[str, WebSocketServerProtocol] = {}
        self._lock = asyncio.Lock()

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
            payload = self._jwt_service.decode(token)
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

        await self._broadcast_user_status(email, True)

    async def _unregister(
        self, email: str, websocket: WebSocketServerProtocol
    ) -> None:
        async with self._lock:
            if self._clients.get(email) is websocket:
                self._clients.pop(email, None)

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

        await self._send_to(recipient, payload)

    async def _send_to(self, email: str, payload: dict[str, Any]) -> None:
        async with self._lock:
            recipient = self._clients.get(email)

        if recipient:
            await self._safe_send(recipient, payload)

    async def _send_user_list(
        self, websocket: WebSocketServerProtocol
    ) -> None:
        async with self._lock:
            users = list(self._clients.keys())

        payload = {
            "type": "user_list",
            "users": [{"email": user, "online": True} for user in users],
        }
        await self._safe_send(websocket, payload)

    async def _broadcast_user_status(self, email: str, online: bool) -> None:
        async with self._lock:
            sockets = list(self._clients.values())

        payload = {"type": "user_status", "email": email, "online": online}
        await asyncio.gather(
            *(self._safe_send(socket, payload) for socket in sockets),
            return_exceptions=True,
        )

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

    chat_hub = ChatHub(JwtService(jwt_secret))

    logger.info(f"Starting ws server on {host}:{port}")
    async with serve(chat_hub.handler, host, port, max_size=2**20):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
