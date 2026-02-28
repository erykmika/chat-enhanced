from unittest.mock import Mock

import pytest
from flask import Flask
from sqlalchemy import delete, select

from backend.common.jwt import JwtService
from backend.webapp.auth.domain.enums import Role
from backend.webapp.auth.infrastructure.api import auth_bp
from backend.webapp.auth.infrastructure.external import (
    UserConfirmationMailDelivery,
)
from backend.webapp.auth.infrastructure.models import Confirmation, User
from backend.webapp.chat.api import chat_bp
from backend.webapp.config import JWT_SECRET
from backend.webapp.database import db


@pytest.fixture
def app(sql_session):
    app = Flask(__name__)
    app.config.update(
        {
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "TESTING": True,
        }
    )
    db.init_app(app)
    db.session = sql_session
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_invalid_login_data_results_in_401(client):
    response = client.post(
        "/auth/login", json={"email": "aaa", "password": "123"}
    )
    assert response.status_code == 401


def test_registered_user_has_confirmation_token_stored(client, sql_session):
    UserConfirmationMailDelivery.send_confirmation = Mock()

    email = "fancymail@mailservice.int"
    response = client.post(
        "/auth/register",
        json={"email": email, "password": "12312121212121212121212"},
    )

    assert response.status_code == 201

    result = sql_session.execute(
        select(Confirmation).where(Confirmation.email == email)
    ).scalar_one_or_none()

    assert result is not None

    assert result.email == email


def test_confirmation_token_is_removed_user_is_active(client, sql_session):
    UserConfirmationMailDelivery.send_confirmation = Mock()

    email = "metalsonic@mail.int"

    sql_session.add(Confirmation(email=email, token="token123"))
    sql_session.add(
        User(email=email, hash="212121212", role=Role.user, is_active=False)
    )
    sql_session.commit()

    assert (
        not sql_session.execute(select(User).where(User.email == email))
        .scalar_one_or_none()
        .is_active
    )

    response = client.post(
        "/auth/confirm", json={"email": email, "token": "token123"}
    )

    assert response.status_code == 200

    result = sql_session.execute(
        select(Confirmation).where(Confirmation.email == email)
    ).scalar_one_or_none()

    assert result is None

    assert (
        sql_session.execute(select(User).where(User.email == email))
        .scalar_one_or_none()
        .is_active
    )


def test_confirmation_mail_contains_valid_confirmation_url(
    client, monkeypatch
):
    sent = {}

    def _fake_send_confirmation(self, email: str, token: str) -> None:  # noqa: ARG001
        sent["email"] = email
        sent["token"] = token

    # Provide a realistic frontend base URL.
    monkeypatch.setattr(
        "backend.webapp.auth.infrastructure.external.FRONTEND_ROOT_DOMAIN",
        "https://frontend.example",
    )
    monkeypatch.setattr(
        UserConfirmationMailDelivery,
        "send_confirmation",
        _fake_send_confirmation,
    )

    # NOTE: RegistrationService uses a strict email regex that doesn't allow '+'.
    email = "user.tag@mailservice.int"
    response = client.post(
        "/auth/register",
        json={"email": email, "password": "12312121212121212121212"},
    )
    assert response.status_code == 201

    from backend.webapp.auth.infrastructure.external import (
        _build_confirmation_url,
    )

    url = _build_confirmation_url(
        "https://frontend.example/", token=sent["token"], email=sent["email"]
    )
    assert url.startswith("https://frontend.example/confirm/")
    assert "?email=" in url
    assert "user.tag%40mailservice.int" in url


def _auth_header(email: str) -> dict[str, str]:
    assert JWT_SECRET
    token = JwtService(JWT_SECRET).encode({"email": email, "role": Role.user})
    return {"Authorization": f"Bearer {token}"}


def test_list_users_requires_auth(client):
    response = client.get("/chat/users")
    assert response.status_code == 401
    assert response.get_json() == {"error": "unauthorized"}


def test_list_users_excludes_requester_and_inactive_users(client, sql_session):
    sql_session.execute(delete(User))
    sql_session.commit()

    requester = User(
        email="owner@example.com",
        hash="hash",
        role=Role.user,
        is_active=True,
    )
    active_peer = User(
        email="active@example.com",
        hash="hash",
        role=Role.user,
        is_active=True,
    )
    inactive_peer = User(
        email="inactive@example.com",
        hash="hash",
        role=Role.user,
        is_active=False,
    )

    sql_session.add_all([requester, active_peer, inactive_peer])
    sql_session.commit()

    response = client.get("/chat/users", headers=_auth_header(requester.email))

    assert response.status_code == 200
    payload = response.get_json()
    assert payload is not None
    assert {user["email"] for user in payload["users"]} == {
        "active@example.com"
    }
