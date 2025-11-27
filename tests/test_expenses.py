from decimal import Decimal
from typing import override

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select

from app import models
from app.database import get_session
from app.main import app
from app.models import Group, User, UserGroup

TEST_DATABASE_URL = "postgresql://postgres:password@localhost:5432/postgres"

engine = create_engine(TEST_DATABASE_URL, echo=False)
SQLModel.metadata.drop_all(engine, checkfirst=True)
SQLModel.metadata.create_all(engine, checkfirst=True)


class NoCommitSession(Session):
    @override
    def commit(self):
        self.flush()


@pytest.fixture(scope="module")
def global_session():
    with NoCommitSession(engine) as session:
        yield session
        session.rollback()


@pytest.fixture
def session(global_session: Session):
    with global_session.begin_nested() as savepoint:
        yield global_session
        savepoint.rollback()


@pytest.fixture()
def client(session):
    def get_session_overide():
        return session

    # Ques :Why does this dependency injection feels weird? Why would you need that actual object "get_sesson"
    app.dependency_overrides[get_session] = get_session_overide
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


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


@pytest.fixture(scope="module", name="groups")
def fixture_groups(global_session):
    group1 = models.Group(name="Goa Trip")
    group2 = models.Group(name="Andamans Trip")
    global_session.add(group1)
    global_session.add(group2)
    global_session.commit()

    global_session.refresh(group1)
    global_session.refresh(group2)
    return [group1, group2]


@pytest.fixture(scope="module")
def expenses(global_session: Session, groups, users):
    """Add users to group and add multiple expenses for each user in each group"""
    expenses_list = []
    user_group_list = []

    # Total of 8 expenses 2*2*2 since we have 2 users and 2 groups and 2 expenses per each
    for u in users:
        for g in groups:
            user_group = UserGroup(user_id=u.id, group_id=g.id)

            expense1 = models.Expense(
                title=f"{u.name} - Lunch ({g.name})",
                amount=Decimal("50.45"),
                group_id=g.id,
                user_id=u.id,
            )
            expense2 = models.Expense(
                title=f"{u.name} - Dinner ({g.name})",
                amount=Decimal("20.45"),
                group_id=g.id,
                user_id=u.id,
            )

            global_session.add(expense1)
            global_session.add(expense2)
            expenses_list.extend([expense1, expense2])
            global_session.add(user_group)
            user_group_list.append(user_group)

    # This is required since it will flush since we intercept commit.
    # Also refresh wont work without flushing and will raise error
    global_session.commit()
    for exp in expenses_list:
        global_session.refresh(exp)
    for ug in user_group_list:
        global_session.refresh(ug)

    return expenses_list


def test_expenses_fixture(expenses): ...


def test_create_expense(client, users, groups):
    user = users[0]
    group = groups[0]
    payload = {
        "title": "Lunch",
        "amount": 50.45,
        "group_id": group.id,
        "user_id": user.id,
    }

    response = client.post("/expenses", json=payload)
    data = response.json()
    assert response.status_code == 200
    assert data["title"] == "Lunch"
    assert (
        data["amount"] == 50.45
    )  # JSON encodes the decimal.Decimal type as string. Fix this
    assert data["group_id"] == group.id
    assert data["user_id"] == user.id


def test_read_user_expenses(client, expenses, users):
    """It should return all the expenses created by the user"""
    user = users[0]
    res = client.get(f"/expenses?user_id={user.id}")
    data = res.json()
    assert isinstance(data, list)
    assert len(data) == 4


def test_user_group_expenses1(client, users, expenses, groups):
    """
    It should return all the expenses created by the user in a provided group
    provided the user is part of the group
    """
    user = users[0]
    group = groups[0]
    res = client.get(f"/expenses?user_id={user.id}&group_id={group.id}")
    data = res.json()
    assert isinstance(data, list)
    assert len(data) == 2


def test_user_group_expenses2(client, users, expenses):
    """
    It should return a 404 error if user is not part of the group
    """
    user = users[0]
    some_none_existing_group = 99
    res = client.get(f"/expenses?user_id={user.id}&group_id={some_none_existing_group}")
    data = res.json()
    assert res.status_code == 404
    assert "No association exists" in data["detail"]
