import pytest
from argon2 import PasswordHasher

from backend.webapp.auth.infrastructure.repository import UsersDatabaseRepository
from backend.webapp.auth.domain.service import AuthenticationService
from backend.webapp.auth.domain.dtos import UserLoginInputDTO
from backend.webapp.auth.domain.enums import LoginStatus
from backend.webapp.auth.infrastructure.models import User


@pytest.fixture
def users_repo(sql_session):
    return UsersDatabaseRepository(sql_session)


@pytest.fixture
def auth_service(users_repo):
    return AuthenticationService(users_repo)


def test_register_and_login_success(auth_service):
    email = "integration@example.com"
    password = "testpass"
    # Register
    user = auth_service.register(email=email, password=password)
    assert user is not None
    assert user.email == email
    # Login
    result = auth_service.login(UserLoginInputDTO(email=email, password=password))
    assert result.status == LoginStatus.successful
    assert result.user.email == email


def test_register_duplicate(auth_service):
    email = "dupe@example.com"
    password = "testpass"
    user1 = auth_service.register(email=email, password=password)
    user2 = auth_service.register(email=email, password=password)
    assert user1 is not None
    assert user2 is None


def test_login_wrong_password(auth_service):
    email = "wrongpass@example.com"
    password = "rightpass"
    auth_service.register(email=email, password=password)
    result = auth_service.login(UserLoginInputDTO(email=email, password="wrongpass"))
    assert result.status == LoginStatus.unauthorized
    assert result.user is None


def test_login_unregistered_user(auth_service):
    result = auth_service.login(
        UserLoginInputDTO(email="nouser@example.com", password="irrelevant")
    )
    assert result.status == LoginStatus.unauthorized
    assert result.user is None


def test_login_inactive_user(users_repo, auth_service):
    password = "irrelevant"
    hasher = PasswordHasher()
    hashed_password = hasher.hash(password)
    user = User(
        email="inactive@example.com", hash=hashed_password, role="user", is_active=False
    )
    users_repo._session.add(user)
    users_repo._session.commit()
    result = auth_service.login(
        UserLoginInputDTO(email="inactive@example.com", password="irrelevant")
    )
    assert result.status == LoginStatus.email_unverified
    assert result.user is None
