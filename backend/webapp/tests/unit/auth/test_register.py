from unittest.mock import Mock

from backend.webapp.auth.domain.dtos import (
    RegisteredUserDTO,
)
from backend.webapp.auth.domain.enums import (
    RegistrationStatus,
    Role,
)
from backend.webapp.auth.domain.service.register import RegistrationService
from backend.webapp.tests.unit.auth.mock import MockUsersRepo  # type: ignore


def test_registration_should_return_dto_with_status():
    repo = MockUsersRepo()
    service = RegistrationService(repo)
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
    service = RegistrationService(repo)

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
