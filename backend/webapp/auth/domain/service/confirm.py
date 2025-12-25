import uuid
from logging import getLogger

from backend.webapp.auth.domain.dtos import UserConfirmationInput
from backend.webapp.auth.domain.ports import (
    ConfirmationRepoInterface,
    UserConfirmationDeliveryInterface,
)


class UserConfirmationException(Exception):
    pass


class UserConfirmationService:
    def __init__(
        self,
        delivery_service: UserConfirmationDeliveryInterface,
        repository: ConfirmationRepoInterface,
    ) -> None:
        self._logger = getLogger(__name__)
        self._delivery = delivery_service
        self._repo = repository

    def send_confirmation(self, email: str) -> None:
        token = str(uuid.uuid4())
        self._repo.store_token_for_user(email, token)
        self._delivery.send_confirmation(email, token)

    def confirm(self, input_dto: UserConfirmationInput) -> bool:
        stored_token = self._repo.get_token_for_user(email=input_dto.email)

        if stored_token is None:
            raise UserConfirmationException("user not found")

        if stored_token == input_dto.token:
            return True
        return False
