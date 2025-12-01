from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.models import User


def test_create_user_api(client: TestClient):
    """Check if the api response is correct"""

    response = client.post("/users", json={"name": "Test User"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test User"
    assert "id" in data


def test_create_user_db(client: TestClient, session: Session):
    """Check if the db has the correct values"""
    response = client.post("/users", json={"name": "Test User"})
    assert response.status_code == 200
    data = response.json()
    db_users = session.exec(select(User)).all()
    assert len(db_users) == 1
    db_user = db_users[0]
    assert data["id"] == db_user.id
    assert db_user.name == "Test User"


def test_read_users(client: TestClient):
    # Create a user first
    client.post("/users", json={"name": "Test User 1"})
    response = client.post("/users", json={"name": "Test User 2"})
    client.post("/users", json={"name": "Test User 3"})

    data = response.json()

    res = client.get(f"/users/{data['id']}")
    assert res.status_code == 200

    user_data = res.json()
    assert isinstance(user_data, dict)
    assert user_data["id"] == data["id"]
    assert user_data["name"] == "Test User 2"
