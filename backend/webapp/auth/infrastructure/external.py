from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr

from backend.webapp.auth.domain.ports import UserConfirmationDeliveryInterface
from backend.webapp.config import (
    FRONTEND_ROOT_DOMAIN,
    MAIL_FROM,
    MAIL_FROM_NAME,
    MAIL_PASSWORD,
    MAIL_PORT,
    MAIL_SERVER,
    MAIL_USERNAME,
)


class UserConfirmationMailDelivery(UserConfirmationDeliveryInterface):
    def __init__(self):
        self._config = ConnectionConfig(
            MAIL_USERNAME=MAIL_USERNAME,
            MAIL_PASSWORD=MAIL_PASSWORD,
            MAIL_FROM=MAIL_FROM,
            MAIL_PORT=MAIL_PORT,
            MAIL_SERVER=MAIL_SERVER,
            MAIL_FROM_NAME=MAIL_FROM_NAME,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
        )

    def send_confirmation(self, email: str, token: str) -> None:
        email: EmailStr  # type: ignore
        message = MessageSchema(
            subject="Confirm your account",
            recipients=[email],
            body=f"Click on this link to confirm your account: {FRONTEND_ROOT_DOMAIN}/confirm/{token}",
            subtype=MessageType.html,
        )

        fm = FastMail(self._config)
        fm.send_message(message)
