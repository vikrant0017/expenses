import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import User
from app.utils import hash_password


@pytest.fixture(name="user")
def create_user(session: Session):
    db_user = User(username="Vikrant", password=hash_password("passpass"))
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def test_signup(client: TestClient):
    response = client.post(
        "/signup", json={"username": "Vikrant", "password": "passpass"}
    )
    data = response.json()
    assert response.status_code == 200
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user_id" in data


def test_login_success(client: TestClient, user):
    response = client.post(
        "/token", data={"username": "Vikrant", "password": "passpass"}
    )
    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user_id" in data


def test_incorrect_username(client: TestClient, user):
    response = client.post(
        "/token", data={"username": "Vikrant", "password": "helloworld"}
    )
    data = response.json()
    assert response.status_code == 401
    headers = response.headers

    assert headers.get("WWW-Authenticate") == "Bearer"
    assert data.get("detail") == "Unauthorized user"


def test_incorrect_password(client: TestClient, user):
    response = client.post("/token", data={"username": "Vicky", "password": "passpass"})
    data = response.json()
    assert response.status_code == 401
    headers = response.headers

    assert headers.get("WWW-Authenticate") == "Bearer"
    assert data.get("detail") == "Unauthorized user"
