import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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
