from abc import ABC, abstractmethod

from backend.webapp.auth.domain.dtos import RegisteredUserDTO


class UsersRepoInterface(ABC):
    @abstractmethod
    def get_user_by_email(self, email: str) -> RegisteredUserDTO | None:
        pass

    @abstractmethod
    def create_user(
        self, email: str, password_hash: str, role: str
    ) -> RegisteredUserDTO:
        pass
