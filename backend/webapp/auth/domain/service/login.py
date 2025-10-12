from argon2 import PasswordHasher
from argon2 import exceptions as argon2_exceptions

from backend.webapp.auth.domain.dtos import (
    AuthenticatedUserDTO,
    LoginResultDTO,
    UserLoginInputDTO,
)
from backend.webapp.auth.domain.enums import LoginStatus
from backend.webapp.auth.domain.users import UsersRepoInterface


class LoginService:
    def __init__(self, users_repo: UsersRepoInterface) -> None:
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
