import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app import models


@pytest.fixture(scope="module", name="users")
def fixture_users(global_session: Session):
    user1 = models.User(name="Foo")
    user2 = models.User(name="Bar")
    global_session.add(user1)
    global_session.add(user2)
    global_session.commit()

    global_session.refresh(user1)
    global_session.refresh(user2)
    return [user1, user2]


# TODO: Create some helpers for these fixtures
@pytest.fixture(scope="module", name="groups")
def fixture_groups(global_session, users):
    """
    Add some groups and associate each group with a user
    """
    group1 = models.Group(name="Group 1")
    group2 = models.Group(name="Group 2")
    group3 = models.Group(name="Group 3")

    global_session.add(group1)
    global_session.add(group2)
    global_session.add(group3)

    global_session.flush()
    global_session.refresh(group1)
    global_session.refresh(group2)
    global_session.refresh(group3)

    user_group1 = models.UserGroup(user_id=users[0].id, group_id=group1.id)
    user_group2 = models.UserGroup(user_id=users[0].id, group_id=group2.id)
    user_group3 = models.UserGroup(user_id=users[1].id, group_id=group3.id)

    global_session.add(user_group1)
    global_session.add(user_group2)
    global_session.add(user_group3)

    global_session.flush()

    return [group1, group2]


def test_create_group(client: TestClient, users, session):
    """
    It should create a group and also add the user to the group implicity
    """
    user = users[0]
    response = client.post("/groups", json={"user_id": user.id, "name": "Goa"})
    data = response.json()
    assert response.status_code == 200
    assert data["name"] == "Goa"
    assert "id" in data

    # Test that a user is associated with the group
    user_group = session.exec(
        select(models.UserGroup).where(
            models.UserGroup.user_id == user.id, models.UserGroup.group_id == data["id"]
        )
    ).all()
    assert len(user_group) == 1
    assert user_group[0].user_id == user.id
    assert user_group[0].group_id == data["id"]


def test_read_group_user_1(client: TestClient, users, groups):
    response = client.get(f"/groups?user_id={users[0].id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_read_group_user_2(client: TestClient, users, groups):
    response = client.get(f"/groups?user_id={users[1].id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_read_group_user_3(client: TestClient, users, groups):
    non_existing_user_id = 100
    response = client.get(f"/groups?user_id={non_existing_user_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
