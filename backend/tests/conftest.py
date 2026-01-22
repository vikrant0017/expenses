import os
from typing import override

import pytest
from dotenv import load_dotenv
from faker import Faker
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.crud.groups import add_user, create_group
from app.crud.users import create_user
from app.database import get_session
from app.deps import get_current_user
from app.main import app
from app.models import GroupCreate, User, UserCreate

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


@pytest.fixture
def user_factory(request):
    """Factory fixture that creates a new user on each call"""

    def _create_user(username: str | None = None, password: str | None = None):
        faker = Faker()
        session = request.getfixturevalue("session")
        user = UserCreate(
            username=username or faker.user_name(),
            password=password or faker.password(8),
        )
        db_user = create_user(session, user)
        return db_user

    return _create_user


@pytest.fixture
def auth_client_factory(request):
    """Factory fixture that returns a callable for creating an authenticated TestClient.

    The returned factory creates a TestClient whose dependencies are overridden:
    - get_current_user is set to a function that returns the provided user_id.
    - get_session is set to return the test's Session fixture.

    Note: app is a single shared FastAPI instance, so each override replaces the previous one.
    As a result, multiple clients created by this factory will share the most recent dependency
    overrides (including the same get_current_user function). Do not rely on creating multiple
    concurrent authenticated clients with different users in the same test; create them
    sequentially or ensure earlier clients are no longer needed before creating new ones.
    """

    def _create_user_with_client(user_id: str):
        session = request.getfixturevalue("session")

        app.dependency_overrides[get_current_user] = lambda: user_id

        def get_session_override():
            return session

        app.dependency_overrides[get_session] = get_session_override
        client = TestClient(app)

        return client

    yield _create_user_with_client
    app.dependency_overrides.clear()


@pytest.fixture
def group_factory(request):
    """Factory fixture that creates a new user and authenticated client on each call"""

    def _create_user_with_group(user_id: int, group_name: str | None = None):
        faker = Faker()
        session = request.getfixturevalue("session")

        group = GroupCreate(name=group_name or faker.color_name())
        db_group = create_group(session, user_id, group)

        return db_group

    return _create_user_with_group


@pytest.fixture
def user_group_factory(request):
    """Factory fixture that creates a new user and authenticated client on each call"""

    def _add_user_to_group(user_id: int, group_id: int):
        session = request.getfixturevalue("session")

        return add_user(session, group_id, user_id)

    return _add_user_to_group


@pytest.fixture(name="group")
def get_group(session: Session, authenticated_user: User):
    group = GroupCreate(name="Group 1")
    return create_group(session, authenticated_user.id, group)  # ty: ignore[invalid-argument-type]
