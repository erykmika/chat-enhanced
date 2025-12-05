import pytest
from argon2 import PasswordHasher

from backend.webapp.auth.domain.dtos import UserLoginInputDTO
from backend.webapp.auth.domain.enums import LoginStatus, RegistrationStatus
from backend.webapp.auth.domain.service.login import LoginService
from backend.webapp.auth.domain.service.register import RegistrationService
from backend.webapp.auth.infrastructure.models import User
from backend.webapp.auth.infrastructure.repository import (
    UsersDatabaseRepository,
)


@pytest.fixture
def users_repo(sql_session):
    return UsersDatabaseRepository(sql_session)


@pytest.fixture
def login_service(users_repo):
    return LoginService(users_repo)


@pytest.fixture
def register_service(users_repo):
    return RegistrationService(users_repo)


def test_register_and_login_success(login_service, register_service):
    email = "integration@example.com"
    password = "testpass"
    # Register
    result = register_service.register(email=email, password=password)
    assert result.status == RegistrationStatus.success
    # Login
    result = login_service.login(
        UserLoginInputDTO(email=email, password=password)
    )
    assert result.status == LoginStatus.email_unverified
    assert result.user is None


def test_register_duplicate(register_service):
    email = "dupe@example.com"
    password = "testpass"
    result1 = register_service.register(email=email, password=password)
    result2 = register_service.register(email=email, password=password)
    assert result1.status == RegistrationStatus.success
    assert result2.status == RegistrationStatus.failure


def test_login_wrong_password(login_service, register_service):
    email = "wrongpass@example.com"
    password = "rightpass"
    register_service.register(email=email, password=password)
    result = login_service.login(
        UserLoginInputDTO(email=email, password="wrongpass")
    )
    assert result.status == LoginStatus.unauthorized
    assert result.user is None


def test_login_unregistered_user(login_service):
    result = login_service.login(
        UserLoginInputDTO(email="nouser@example.com", password="irrelevant")
    )
    assert result.status == LoginStatus.unauthorized
    assert result.user is None


def test_login_inactive_user(users_repo, login_service):
    password = "irrelevant"
    hasher = PasswordHasher()
    hashed_password = hasher.hash(password)
    user = User(
        email="inactive@example.com",
        hash=hashed_password,
        role="user",
        is_active=False,
    )
    users_repo._session.add(user)
    users_repo._session.commit()
    result = login_service.login(
        UserLoginInputDTO(email="inactive@example.com", password="irrelevant")
    )
    assert result.status == LoginStatus.email_unverified
    assert result.user is None
