import re
from logging import getLogger

import jwt
from argon2 import PasswordHasher
from argon2 import exceptions as argon2_exceptions

from backend.webapp.auth.domain.dtos import (
    AuthenticatedUserDTO,
    LoginResultDTO,
    RegistrationResultDto,
    UserLoginInputDTO,
)
from backend.webapp.auth.domain.enums import LoginStatus, RegistrationStatus
from backend.webapp.auth.domain.users import UsersRepoInterface


class JwtService:
    def __init__(self, secret_key: str) -> None:
        self._secret_key = secret_key

    def encode(self, payload: dict) -> str:
        return jwt.encode(payload, self._secret_key, algorithm="HS256")

    def decode(self, token: str) -> dict:
        return jwt.decode(token, self._secret_key, algorithms=["HS256"])


class AuthenticationService:
    def __init__(self, users_repo: UsersRepoInterface) -> None:
        self._logger = getLogger(__name__)
        self._users_repo = users_repo

    def login(self, login_data: UserLoginInputDTO) -> LoginResultDTO:
        user = self._users_repo.get_user_by_email(login_data.email)
        if not user:
            return LoginResultDTO(status=LoginStatus.unauthorized)

        hasher = PasswordHasher()
        try:
            hasher.verify(user.password_hash, login_data.password)
        except argon2_exceptions.VerifyMismatchError:
            return LoginResultDTO(status=LoginStatus.unauthorized)

        if not user.is_active:
            return LoginResultDTO(status=LoginStatus.email_unverified)

        auth_user = AuthenticatedUserDTO(email=user.email, role=user.role)
        return LoginResultDTO(status=LoginStatus.successful, user=auth_user)

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
