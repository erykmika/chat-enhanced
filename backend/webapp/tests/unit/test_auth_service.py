# type: ignore

from unittest.mock import Mock

from argon2 import PasswordHasher

from backend.webapp.auth.domain.dtos import (
    LoginResultDTO,
    RegisteredUserDTO,
    UserLoginInputDTO,
)
from backend.webapp.auth.domain.enums import (
    LoginStatus,
    RegistrationStatus,
    Role,
)
from backend.webapp.auth.domain.service import AuthenticationService
from backend.webapp.auth.domain.users import UsersRepoInterface


class MockUsersRepo(UsersRepoInterface):
    def create_user(
        self, email: str, password: str, role: str
    ) -> RegisteredUserDTO:
        pass

    def get_user_by_email(self, email: str) -> RegisteredUserDTO:
        pass


def test_login_should_return_authenticated_user_dto():
    repo = MockUsersRepo()
    service = AuthenticationService(repo)
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
    service = AuthenticationService(repo)
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


def test_registration_should_return_dto_with_status():
    repo = MockUsersRepo()
    service = AuthenticationService(repo)
    EMAIL = "newuser@example.com"
    PASSWORD = "securepass"

    # Simulate user does not exist
    repo.get_user_by_email = Mock(return_value=None)
    repo.create_user = Mock(
        return_value=RegisteredUserDTO(
            email=EMAIL,
            password_hash="irrelevant",
            role=Role("user"),
            is_active=True,
        )
    )
    result = service.register(email=EMAIL, password=PASSWORD)
    assert result is not None
    assert result.status == RegistrationStatus.success

    # Simulate user already exists
    repo.get_user_by_email = Mock(
        return_value=RegisteredUserDTO(
            email=EMAIL,
            password_hash="irrelevant",
            role=Role("user"),
            is_active=True,
        )
    )
    result = service.register(email=EMAIL, password=PASSWORD)
    assert result.status == RegistrationStatus.failure


def test_registration_rejects_invalid_email():
    repo = MockUsersRepo()
    repo.get_user_by_email = Mock(return_value=None)
    repo.create_user = Mock()
    service = AuthenticationService(repo)

    invalid_emails = [
        "plainaddress",
        "@missingusername.com",
        "username@.com",
        "username@domain",
        "username@domain,com",
        "username@domain..com",
    ]
    for email in invalid_emails:
        result = service.register(email=email, password="irrelevant")
        assert result.status == RegistrationStatus.failure
        repo.create_user.assert_not_called()

    valid_email = "valid.user@example.com"
    repo.create_user.return_value = RegisteredUserDTO(
        email=valid_email,
        password_hash="irrelevant",
        role=Role("user"),
        is_active=True,
    )
    result = service.register(email=valid_email, password="irrelevant")
    assert result.status == RegistrationStatus.success
