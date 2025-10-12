# type: ignore

from backend.webapp.auth.domain.dtos import RegisteredUserDTO
from backend.webapp.auth.domain.users import UsersRepoInterface


class MockUsersRepo(UsersRepoInterface):
    def create_user(
        self, email: str, password: str, role: str
    ) -> RegisteredUserDTO:
        pass

    def get_user_by_email(self, email: str) -> RegisteredUserDTO:
        pass
