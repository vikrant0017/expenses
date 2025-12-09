from fastapi.testclient import TestClient

from app.models import Group, User


def test_create_member_fail(user_factory, auth_client_factory):
    """It should fail to create a member if user is not a member of the group"""

    user: User = user_factory()
    user_to_add: User = user_factory()

    client: TestClient = auth_client_factory(user.id)
    non_existing_group_id = 1  # Some group that user is not part of
    response = client.post(
        f"/groups/{non_existing_group_id}/members", json={"id": user_to_add.id}
    )
    assert response.status_code == 403


def test_create_member_success(user_factory, auth_client_factory, group_factory):
    """It should succeed to create member if user is a member of the group"""

    user: User = user_factory()
    user_to_add: User = user_factory()

    client: TestClient = auth_client_factory(user.id)
    group: Group = group_factory(user_id=user.id)

    response = client.post(f"/groups/{group.id}/members", json={"id": user_to_add.id})
    assert response.status_code == 200
