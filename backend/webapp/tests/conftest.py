import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from backend.webapp.auth.domain.ports import UserConfirmationDeliveryInterface
from backend.webapp.auth.domain.service.confirm import UserConfirmationService
from backend.webapp.auth.domain.service.register import RegistrationService
from backend.webapp.auth.infrastructure.repository import (
    ConfirmationDatabaseRepository,
)
from backend.webapp.database.sql import db


@pytest.fixture(scope="session")
def sql_session():
    engine = create_engine("sqlite://", echo=True)
    db.metadata.create_all(engine)
    maker = sessionmaker(bind=engine)
    Session = scoped_session(maker)
    try:
        yield Session
    finally:
        Session.remove()
        db.metadata.drop_all(engine)


class MockDeliveryService(UserConfirmationDeliveryInterface):
    def send_confirmation(self, email: str, token: str) -> None:
        pass


@pytest.fixture
def delivery_service():
    return MockDeliveryService()


@pytest.fixture
def confirm_repo(sql_session):
    return ConfirmationDatabaseRepository(sql_session)


@pytest.fixture
def register_service(users_repo, confirm_repo, delivery_service):
    return RegistrationService(
        users_repo,
        confirmation_repository=confirm_repo,
        delivery_service=delivery_service,
    )


@pytest.fixture
def confirm_service(confirm_repo, delivery_service):
    return UserConfirmationService(
        delivery_service=delivery_service, repository=confirm_repo
    )
