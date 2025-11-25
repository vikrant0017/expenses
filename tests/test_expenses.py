import pytest
from fastapi.testclient import TestClient
from starlette.types import Scope

from app import models
from app.database import get_session
from app.main import app

client = TestClient(app)


@pytest.fixture
def session():
    session_gen = get_session()
    return next(session_gen)


@pytest.fixture()
def user(session):
    user = models.User(name="Vikrant")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture()
def group(session):
    group = models.Group(name="Goa")
    session.add(group)
    session.commit()
    session.refresh(group)
    return group


def test_create_expense(user, group):
    # get_session() is a generator (FastAPI dependency). Advance it to obtain the Session it yields,
    # and ensure we close the generator to run any cleanup code.
    payload = {
        "title": "Lunch",
        "amount": 50.45,
        "group_id": group.id,
        "user_id": user.id,
    }

    response = client.post("/expenses", json=payload)
    data = response.json()
    print(data)
    assert response.status_code == 200
    assert data["title"] == "Lunch"
    assert (
        data["amount"] == 50.45
    )  # JSON encodes the decimal.Decimal type as string. Fix this
    assert data["group_id"] == group.id
    assert data["user_id"] == user.id

    # print(user.id)
    # print(group.id)


# def test_read_expense():
#     session_gen = get_session()
#     session = next(session_gen)


# Re-writing the test to use session fixture for setup
# def test_create_expense_full(client: TestClient, session):
#     from app.models import User, Group

#     user = User(name="Alice")
#     session.add(user)

#     group = Group(name="Lunch Group")
#     session.add(group)

#     session.commit()
#     session.refresh(user)
#     session.refresh(group)


# def test_read_expenses(client: TestClient, session):
#     from app.models import User, Group, Expense

#     user = User(name="Bob")
#     session.add(user)
#     group = Group(name="Dinner Group")
#     session.add(group)
#     session.commit()
#     session.refresh(user)
#     session.refresh(group)

#     # Create expense via API
#     payload = {
#         "title": "Dinner",
#         "amount": "100.00",
#         "group_id": group.id,
#         "user_id": user.id,
#     }
#     client.post("/expenses", json=payload)

#     response = client.get("/expenses")
#     data = response.json()
#     pprint(data)
#     assert response.status_code == 200
#     assert len(data) >= 1
