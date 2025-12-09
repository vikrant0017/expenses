from typing import Callable

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app import models


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
