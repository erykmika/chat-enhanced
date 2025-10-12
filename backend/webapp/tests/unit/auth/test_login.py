from unittest.mock import Mock

from argon2 import PasswordHasher

from backend.webapp.auth.domain.dtos import (
    LoginResultDTO,
    RegisteredUserDTO,
    UserLoginInputDTO,
)
from backend.webapp.auth.domain.enums import LoginStatus, Role
from backend.webapp.auth.domain.service.login import LoginService
from backend.webapp.tests.unit.auth.mock import MockUsersRepo  # type: ignore


def test_login_should_return_authenticated_user_dto():
    repo = MockUsersRepo()
    service = LoginService(repo)
    EMAIL = "some@example.com"
    PASSWORD = "password123"

    hasher = PasswordHasher()
    password_hash = hasher.hash(PASSWORD)

    repo.get_user_by_email = Mock(
        return_value=RegisteredUserDTO(
            email=EMAIL,
            password_hash=password_hash,
            role=Role("user"),
            is_active=True,
        )
    )

    result = service.login(
        login_data=UserLoginInputDTO(email=EMAIL, password=PASSWORD)
    )

    assert isinstance(result, LoginResultDTO)
    assert result.status == LoginStatus.successful
    assert result.user is not None
    assert result.user.email == EMAIL
    assert result.user.role == Role("user")


def test_login_should_return_none_for_invalid_credentials():
    repo = MockUsersRepo()
    service = LoginService(repo)
    EMAIL = "some@example.com"
    PASSWORD = "password123"

    repo.get_user_by_email = Mock(return_value=None)
    result = service.login(
        login_data=UserLoginInputDTO(email=EMAIL, password=PASSWORD)
    )
    assert isinstance(result, LoginResultDTO)
    assert result.status == LoginStatus.unauthorized
    assert result.user is None

    # Test wrong password
    hasher = PasswordHasher()
    password_hash = hasher.hash("otherpassword")
    repo.get_user_by_email = Mock(
        return_value=RegisteredUserDTO(
            email=EMAIL,
            password_hash=password_hash,
            role=Role("user"),
            is_active=True,
        )
    )
    result = service.login(
        login_data=UserLoginInputDTO(email=EMAIL, password=PASSWORD)
    )
    assert result.status == LoginStatus.unauthorized
    assert result.user is None

    # Test inactive user
    password_hash = hasher.hash(PASSWORD)
    repo.get_user_by_email = Mock(
        return_value=RegisteredUserDTO(
            email=EMAIL,
            password_hash=password_hash,
            role=Role("user"),
            is_active=False,
        )
    )
    result = service.login(
        login_data=UserLoginInputDTO(email=EMAIL, password=PASSWORD)
    )
    assert result.status == LoginStatus.email_unverified
    assert result.user is None
