from typing import Any

import jwt
from flask import Blueprint, jsonify, request
from sqlalchemy import select

from backend.webapp.auth.infrastructure.models import User
from backend.webapp.config import JWT_SECRET
from backend.webapp.database import db

chat_bp = Blueprint("chat", __name__, url_prefix="/chat")


def _get_bearer_token() -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header.split(" ", 1)[1].strip()


def _decode_token(token: str) -> dict[str, Any] | None:
    try:
        assert JWT_SECRET
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return None


def _get_current_email() -> str | None:
    token = _get_bearer_token()
    if not token:
        return None
    payload = _decode_token(token)
    if not payload:
        return None
    email = payload.get("email")
    if not isinstance(email, str) or not email:
        return None
    return email


@chat_bp.route("/users", methods=["GET"])
def list_users():
    email = _get_current_email()
    if not email:
        return jsonify({"error": "unauthorized"}), 401

    users = (
        db.session.execute(
            select(User.email).where(
                User.is_active.is_(True),
                User.email != email,
            )
        )
        .scalars()
        .all()
    )

    return jsonify({"users": [{"email": user_email} for user_email in users]})
