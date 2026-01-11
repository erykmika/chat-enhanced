from flask_sqlalchemy.session import Session
from sqlalchemy import delete, select

from backend.webapp.auth.domain.dtos import RegisteredUserDTO
from backend.webapp.auth.domain.enums import Role
from backend.webapp.auth.domain.ports import (
    ConfirmationRepoInterface,
    UsersRepoInterface,
)
from backend.webapp.auth.infrastructure.models import Confirmation, User


class UsersDatabaseRepository(UsersRepoInterface):
    def __init__(self, session: Session):
        self._session = session

    def get_user_by_email(self, email: str) -> RegisteredUserDTO | None:
        user = self._session.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()
        if user:
            return RegisteredUserDTO(
                email=user.email,
                role=user.role,
                password_hash=user.hash,
                is_active=user.is_active,
            )
        else:
            return None

    def create_user(
        self, email: str, password_hash: str, role: str, is_active: bool
    ) -> RegisteredUserDTO:
        new_user = User(
            email=email, hash=password_hash, role=role, is_active=is_active
        )
        self._session.add(new_user)
        self._session.commit()
        return RegisteredUserDTO(
            email=new_user.email,
            role=Role(new_user.role),
            password_hash=new_user.hash,
            is_active=new_user.is_active,
        )


class ConfirmationDatabaseRepository(ConfirmationRepoInterface):
    def __init__(self, session: Session) -> None:
        self._session = session

    def _get_user(self, email: str) -> User | None:
        return self._session.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

    def store_token_for_user(self, email: str, token: str) -> None:
        self._session.add(Confirmation(email=email, token=token))
        self._session.commit()

    def get_token_for_user(self, email: str) -> str | None:
        return self._session.execute(
            select(Confirmation.token).where(Confirmation.email == email)
        ).scalar_one_or_none()

    def activate_user(self, email: str) -> None:
        user = self._get_user(email)
        if user is None:
            raise ValueError("user not found")
        else:
            user.is_active = True
            self._session.commit()
            return None

    def remove_confirmation_token(self, email: str) -> None:
        self._session.execute(
            delete(Confirmation).where(Confirmation.email == email)
        )
        self._session.commit()
