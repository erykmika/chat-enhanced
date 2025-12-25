from abc import ABC, abstractmethod

from backend.webapp.auth.domain.dtos import RegisteredUserDTO


class UsersRepoInterface(ABC):
    @abstractmethod
    def get_user_by_email(self, email: str) -> RegisteredUserDTO | None:
        pass

    @abstractmethod
    def create_user(
        self, email: str, password_hash: str, role: str, is_active: bool
    ) -> RegisteredUserDTO:
        pass


class ConfirmationRepoInterface(ABC):
    @abstractmethod
    def store_token_for_user(self, email: str, token: str) -> None:
        pass

    @abstractmethod
    def get_token_for_user(self, email: str) -> str | None:
        pass


class UserConfirmationDeliveryInterface(ABC):
    @abstractmethod
    def send_confirmation(self, email: str, token: str) -> None:
        pass
