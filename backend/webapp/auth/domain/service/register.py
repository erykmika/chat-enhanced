import re

from argon2 import PasswordHasher

from backend.webapp.auth.domain.dtos import RegistrationResultDto
from backend.webapp.auth.domain.enums import RegistrationStatus
from backend.webapp.auth.domain.users import UsersRepoInterface


class RegistrationService:
    def __init__(self, users_repo: UsersRepoInterface) -> None:
        self._users_repo = users_repo

    @staticmethod
    def is_valid_email(email: str) -> bool:
        pattern = r"^(?!.*\.\.)[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(pattern, email) is not None

    def register(self, email: str, password: str) -> RegistrationResultDto:
        if not self.is_valid_email(email):
            return RegistrationResultDto(
                status=RegistrationStatus.failure,
                reason="user with this email already exists",
            )
        if self._users_repo.get_user_by_email(email):
            return RegistrationResultDto(
                status=RegistrationStatus.failure, reason="invalid email"
            )
        hasher = PasswordHasher()
        password_hash = hasher.hash(password)
        self._users_repo.create_user(
            email=email, password_hash=password_hash, role="user"
        )
        return RegistrationResultDto(status=RegistrationStatus.success)
