import pytest
from flask import Flask

from backend.webapp.auth.infrastructure.api import auth_bp
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
