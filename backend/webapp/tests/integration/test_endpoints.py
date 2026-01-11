from unittest.mock import Mock

import pytest
from flask import Flask
from sqlalchemy import select

from backend.webapp.auth.domain.enums import Role
from backend.webapp.auth.infrastructure.api import auth_bp
from backend.webapp.auth.infrastructure.external import (
    UserConfirmationMailDelivery,
)
from backend.webapp.auth.infrastructure.models import Confirmation, User
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
