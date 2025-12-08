from typing import Callable

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app import models
from app.crud.groups import create_group
from app.crud.users import create_user
from app.database import get_session
from app.deps import get_current_user
from app.main import app
from app.models import GroupCreate, User, UserCreate


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

    def _create_user_with_group(user_id: int, group_name: str):
        session = request.getfixturevalue("session")

        # Create user
        group = GroupCreate(name=group_name)
        db_group = create_group(session, user_id, group)

        return db_group

    yield _create_user_with_group
    app.dependency_overrides.clear()


@pytest.fixture(name="group")
def get_group(session: Session, authenticated_user: User):
    group = GroupCreate(name="Group 1")
    return create_group(session, authenticated_user.id, group)  # pyright: ignore[reportArgumentType]


# --- Tests ---
def test_fail_expense_create_unath_user(client, session: Session):
    response = client.post("/groups", json={"name": "Group1"})
    assert response.status_code == 401


def test_create_group(user_factory, auth_client_factory, session: Session):
    """It should create a group and also add the user to the group implicity"""

    user = user_factory("User1", "pass1")
    client_with_auth = auth_client_factory(user.id)

    response = client_with_auth.post("/groups", json={"name": "Group1"})
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Group1"
    assert "id" in data

    # Test that a user is associated with the group
    user_group = session.exec(
        select(models.UserGroup).where(
            models.UserGroup.user_id == user.id,
            models.UserGroup.group_id == data["id"],
        )
    ).all()

    assert len(user_group) == 1
    assert user_group[0].user_id == user.id
    assert user_group[0].group_id == data["id"]


def test_user_can_read_only_own_groups(
    auth_client_factory: Callable[[int], TestClient], user_factory, group_factory
):
    user1 = user_factory("User1", "pass1")
    user2 = user_factory("User2", "pass2")

    u1g1 = group_factory(user1.id, "User1Group1")
    u1g2 = group_factory(user1.id, "User1Group2")
    u2g1 = group_factory(user2.id, "User2Group1")
    u2g2 = group_factory(user2.id, "User2Group2")

    # -- User 1 -- #
    client_with_auth1 = auth_client_factory(user1.id)
    response1 = client_with_auth1.get("/groups")
    assert response1.status_code == 200

    data1 = response1.json()
    assert len(data1) == 2

    group_names_1 = {group["name"] for group in data1}
    assert group_names_1 == {u1g1.name, u1g2.name}

    # -- User 2 -- #
    client_with_auth2 = auth_client_factory(user2.id)
    response2 = client_with_auth2.get("/groups")
    assert response2.status_code == 200

    data2 = response2.json()
    assert len(data2) == 2

    group_names_2 = {group["name"] for group in data2}
    assert group_names_2 == {u2g1.name, u2g2.name}
