import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def sql_session():
    engine = create_engine("sqlite:///:memory:", echo=True)
    maker = sessionmaker(bind=engine)
    session = maker()
    try:
        yield session
        session.rollback()
    finally:
        session.close()
