from pydantic import BaseModel

from backend.webapp.auth.domain.enums import Role


class UserLoginInputDTO(BaseModel):
    email: str
    password: str


class RegisteredUserDTO(BaseModel):
    email: str
    role: Role
    password: str


class AuthenticatedUserDTO(BaseModel):
    email: str
    role: Role
