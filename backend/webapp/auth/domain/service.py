from logging import getLogger

from argon2 import PasswordHasher, exceptions as argon2_exceptions

from backend.webapp.auth.domain.dtos import (
    UserLoginInputDTO,
    AuthenticatedUserDTO,
    LoginResultDTO,
)
from backend.webapp.auth.domain.enums import LoginStatus
from backend.webapp.auth.domain.users import UsersRepoInterface


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

    def register(self, email: str, password: str) -> AuthenticatedUserDTO | None:
        # Check if user already exists
        if self._users_repo.get_user_by_email(email):
            return None
        hasher = PasswordHasher()
        password_hash = hasher.hash(password)
        # Create user with default role 'user'
        user = self._users_repo.create_user(
            email=email, hash=password_hash, role="user"
        )
        return AuthenticatedUserDTO(email=user.email, role=user.role)
