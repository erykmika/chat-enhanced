from flask_mail import Message

from backend.webapp.auth.domain.ports import UserConfirmationDeliveryInterface
from backend.webapp.config import FRONTEND_ROOT_DOMAIN
from backend.webapp.mails import mailing


class UserConfirmationMailDelivery(UserConfirmationDeliveryInterface):
    def send_confirmation(self, email: str, token: str) -> None:
        message = Message(
            subject="Confirm your account",
            recipients=[email],
            body=f"""
                Use this link to confirm your account:
                {FRONTEND_ROOT_DOMAIN}/confirm/{token}
                """,
        )
        mailing.send(message)
