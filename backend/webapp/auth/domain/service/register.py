import re
from logging import getLogger

from argon2 import PasswordHasher

from backend.webapp.auth.domain.dtos import RegistrationResultDto
from backend.webapp.auth.domain.enums import RegistrationStatus
from backend.webapp.auth.domain.ports import (
    ConfirmationRepoInterface,
    UserConfirmationDeliveryInterface,
    UsersRepoInterface,
)
from backend.webapp.auth.domain.service.confirm import (
    UserConfirmationService,
)


class RegistrationService:
    def __init__(
        self,
        users_repo: UsersRepoInterface,
        delivery_service: UserConfirmationDeliveryInterface,
        confirmation_repository: ConfirmationRepoInterface,
    ) -> None:
        self._users_repo = users_repo
        self._confirmation_service = UserConfirmationService(
            delivery_service=delivery_service,
            repository=confirmation_repository,
        )
        self._logger = getLogger(__name__)

    @staticmethod
    def is_valid_email(email: str) -> bool:
        pattern = r"^(?!.*\.\.)[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(pattern, email) is not None

    def register(self, email: str, password: str) -> RegistrationResultDto:
        if not self.is_valid_email(email):
            return RegistrationResultDto(
                status=RegistrationStatus.failure, reason="invalid email"
            )

        if self._users_repo.get_user_by_email(email):
            return RegistrationResultDto(
                status=RegistrationStatus.failure,
                reason="user with this email already exists",
            )

        hasher = PasswordHasher()
        password_hash = hasher.hash(password)

        self._users_repo.create_user(
            email=email,
            password_hash=password_hash,
            role="user",
            is_active=False,
        )

        self._logger.info(f"User={email} created. Sending confirmation mail")
        self._confirmation_service.send_confirmation(email=email)

        return RegistrationResultDto(status=RegistrationStatus.success)
