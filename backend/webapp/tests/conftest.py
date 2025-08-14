import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.webapp.database.sql import Base


@pytest.fixture(scope="session")
def sql_session():
    engine = create_engine("sqlite:///:memory:", echo=True)
    Base.metadata.create_all(engine)
    maker = sessionmaker(bind=engine)
    session = maker()
    try:
        yield session
        session.rollback()
    finally:
        session.close()
        Base.metadata.drop_all(engine)
