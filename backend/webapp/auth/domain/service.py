from logging import getLogger

from backend.webapp.auth.domain.dtos import UserLoginInputDTO, AuthenticatedUserDTO
from backend.webapp.auth.domain.users import UsersRepoInterface


class AuthenticationService:
    def __init__(self, users_repo: UsersRepoInterface) -> None:
        self._logger = getLogger(__name__)
        self._users_repo = users_repo

    def login(self, login_data: UserLoginInputDTO) -> AuthenticatedUserDTO | None:
        pass

    def register(self, username: str, password: str) -> AuthenticatedUserDTO | None:
        pass