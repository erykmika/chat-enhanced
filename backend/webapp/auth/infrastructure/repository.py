from flask_sqlalchemy.session import Session
from sqlalchemy import select

from backend.webapp.auth.domain.dtos import RegisteredUserDTO
from backend.webapp.auth.domain.enums import Role
from backend.webapp.auth.domain.users import UsersRepoInterface
from backend.webapp.auth.infrastructure.models import User


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
