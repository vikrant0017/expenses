import os
from typing import override

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_session
from app.main import app

TEST_ENV_PATH = os.path.join(os.path.dirname(__file__), "..", ".env.test")
load_dotenv(TEST_ENV_PATH, override=True)
# Database URL
# Assuming postgres user/password from compose.yaml and default port 5432
PG_HOST = os.getenv("PG_HOST", "postgres")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "password")
PG_DB = os.getenv("PG_DB", "postgres")
PG_PORT = os.getenv("PG_PORT", "5432")

DEBUG_SQL = True if os.getenv("DEBUG_SQL") == "true" else False

DATABASE_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"


# Create only one engine per entire test session and intialize the tables
# Each module creates and new global session and runs the tests in sub sessions
@pytest.fixture(scope="session")
def engine():
    engine = create_engine(DATABASE_URL, echo=DEBUG_SQL)
    SQLModel.metadata.drop_all(engine, checkfirst=True)
    SQLModel.metadata.create_all(engine, checkfirst=True)
    return engine


class NoCommitSession(Session):
    @override
    def commit(self):
        self.flush()


@pytest.fixture(scope="module")
def global_session(engine):
    with NoCommitSession(engine) as session:
        yield session
        session.rollback()


@pytest.fixture(scope="function", autouse=True)
def session(global_session: Session):
    with global_session.begin_nested() as savepoint:
        yield global_session
        savepoint.rollback()


@pytest.fixture(scope="function")
def client(request):
    session = request.getfixturevalue(
        "session"
    )  # Use the same session of the specific test

    def get_session_overide():
        return session

    # Ques :Why does this dependency injection feels weird? Why would you need that actual object "get_sesson"
    app.dependency_overrides[get_session] = get_session_overide
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
