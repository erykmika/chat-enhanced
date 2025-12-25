from pydantic import BaseModel

from backend.webapp.auth.domain.enums import (
    LoginStatus,
    RegistrationStatus,
    Role,
)


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


class RegistrationResultDto(BaseModel):
    status: RegistrationStatus
    reason: str | None = None


class UserConfirmationInput(BaseModel):
    email: str
    token: str
