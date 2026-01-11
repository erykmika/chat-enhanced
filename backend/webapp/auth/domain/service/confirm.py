import uuid
from logging import getLogger

from backend.webapp.auth.domain.dtos import (
    UserConfirmationInput,
    UserConfirmationOutput,
)
from backend.webapp.auth.domain.ports import (
    ConfirmationRepoInterface,
    UserConfirmationDeliveryInterface,
)


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

    def confirm(
        self, input_dto: UserConfirmationInput
    ) -> UserConfirmationOutput:
        stored_token = self._repo.get_token_for_user(email=input_dto.email)

        if stored_token is None:
            return UserConfirmationOutput(
                success=False, reason="confirmation not found"
            )

        if stored_token != input_dto.token:
            return UserConfirmationOutput(
                success=False, reason="invalid token"
            )

        try:
            self._repo.activate_user(email=input_dto.email)
        except ValueError:
            return UserConfirmationOutput(
                success=False, reason="user not found"
            )

        self._logger.info("removing token")

        self._repo.remove_confirmation_token(email=input_dto.email)

        self._logger.warning("token removed")

        return UserConfirmationOutput(success=True)
