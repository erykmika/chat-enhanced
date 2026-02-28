from urllib.parse import quote

from flask_mail import Message

from backend.webapp.auth.domain.ports import UserConfirmationDeliveryInterface
from backend.webapp.config import FRONTEND_ROOT_DOMAIN
from backend.webapp.mails import mailing


def _build_confirmation_url(
    frontend_root: str, *, token: str, email: str
) -> str:
    """Build an absolute URL to the frontend confirmation page.

    Ensures we don't end up with double slashes and that the URL is absolute.

    Notes:
      - In local/dev setups, FRONTEND_ROOT_DOMAIN may be unset. In that case we
        fall back to a localhost URL so registration doesn't crash.
    """
    if not frontend_root:
        # Compose default: frontend is exposed on host port 3000.
        frontend_root = "http://localhost:3000"

    # Remove trailing slash so we can safely append path.
    root = frontend_root.rstrip("/")

    # Basic guard so we do not accidentally send non-clickable relative URLs.
    if not (root.startswith("http://") or root.startswith("https://")):
        # Fall back to a working absolute URL rather than crashing the request.
        root = (
            f"http://{root.lstrip('/')}" if root else "http://localhost:3000"
        )

    encoded_email = quote(email, safe="")
    return f"{root}/confirm/{token}?email={encoded_email}"


class UserConfirmationMailDelivery(UserConfirmationDeliveryInterface):
    def send_confirmation(self, email: str, token: str) -> None:
        confirmation_url = _build_confirmation_url(
            FRONTEND_ROOT_DOMAIN, token=token, email=email
        )

        message = Message(
            subject="Confirm your account",
            recipients=[email],
            body=f"""
                Use this link to confirm your account:
                {confirmation_url}
                """,
        )
        mailing.send(message)
