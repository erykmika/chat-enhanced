from enum import StrEnum, auto


class Role(StrEnum):
    user = auto()
    admin = auto()


class LoginStatus(StrEnum):
    successful = auto()
    email_unverified = auto()
    unauthorized = auto()


class RegistrationStatus(StrEnum):
    success = auto()
    failure = auto()
