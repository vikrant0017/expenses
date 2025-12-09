import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.crud.groups import create_group
from app.crud.users import create_user
from app.database import get_session
from app.deps import get_current_user
from app.main import app
from app.models import Group, GroupCreate, User, UserCreate


@pytest.fixture
def user_factory(request):
    """Factory fixture that creates a new user on each call"""

    def _create_user(username: str, password: str = "password"):
        session = request.getfixturevalue("session")
        user = UserCreate(username=username, password=password)
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
        session = request.getfixturevalue("session")

        faker = Faker()

        # Create user
        group = GroupCreate(name=group_name or faker.city())
        db_group = create_group(session, user_id, group)

        return db_group

    yield _create_user_with_group
    app.dependency_overrides.clear()


@pytest.fixture(name="group")
def get_group(session: Session, authenticated_user: User):
    group = GroupCreate(name="Group 1")
    return create_group(session, authenticated_user.id, group)  # pyright: ignore[reportArgumentType]


def test_create_member_fail(user_factory, auth_client_factory):
    """Test should fail to create a member if user is not a member of the group"""
    user: User = user_factory("Vikrant", "Pradhan")
    user_to_add: User = user_factory("Jennie", "Kim")
    client: TestClient = auth_client_factory(user.id)
    group_id = 1  # Some group that user is not part of
    response = client.post(f"/groups/{group_id}/members", json={"id": user_to_add.id})
    assert response.status_code == 403


def test_create_member_success(user_factory, auth_client_factory, group_factory):
    """Test should succeed to create member if user is a member of the group"""
    user: User = user_factory("Vikrant", "Pradhan")
    user_to_add: User = user_factory("Jennie", "Kim")
    client: TestClient = auth_client_factory(user.id)
    group: Group = group_factory(user_id=user.id)
    response = client.post(f"/groups/{group.id}/members", json={"id": user_to_add.id})
    assert response.status_code == 200
