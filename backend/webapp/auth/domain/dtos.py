from pydantic import BaseModel

from backend.webapp.auth.domain.enums import Role, LoginStatus


class UserLoginInputDTO(BaseModel):
    email: str
    password: str


class RegisteredUserDTO(BaseModel):
    email: str
    role: Role
    password_hash: str
    is_active: bool


class AuthenticatedUserDTO(BaseModel):
    email: str
    role: Role


class LoginResultDTO(BaseModel):
    status: LoginStatus
    user: AuthenticatedUserDTO | None = None
