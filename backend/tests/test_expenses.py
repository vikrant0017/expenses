from decimal import Decimal
from typing import List

import pytest
from sqlmodel import Session, select

from app import models
from app.models import Expense, Group, Split, User, UserGroup


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


@pytest.fixture()
def expenses(session: Session, groups, users):
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
                splits=[
                    Split(
                        user_id=u.id,
                        expense_id=1,
                        group_id=g.id,
                        amount=Decimal("30"),
                    ),  # pyright: ignore[reportArgumentType]
                    Split(
                        user_id=u.id,
                        group_id=g.id,
                        expense_id=1,
                        amount=Decimal("70"),
                    ),  # pyright: ignore[reportArgumentType]
                ],
            )

            expense2 = models.Expense(
                title=f"{u.name} - Dinner ({g.name})",
                amount=Decimal("20.45"),
                group_id=g.id,
                user_id=u.id,
                splits=[
                    # Note: expense_id even though is required, is handled by the sql alchemy internally due to relatiionship definition
                    # therefore we are ignoring the error. I am not sure sure how pydantic lets this though
                    Split(  # pyright: ignore[reportCallIssue]
                        user_id=u.id,
                        group_id=g.id,
                        amount=Decimal("40"),
                    ),
                    Split(  # pyright: ignore[reportCallIssue]
                        user_id=u.id,
                        group_id=g.id,
                        amount=Decimal("60"),
                    ),  # pyright: ignore[reportArgumentType]
                ],
            )

            session.add(expense1)
            session.add(expense2)
            expenses_list.extend([expense1, expense2])
            session.add(user_group)
            user_group_list.append(user_group)

    # This is required since it will flush since we intercept commit.
    # Also refresh wont work without flushing and will raise error
    session.commit()
    for exp in expenses_list:
        session.refresh(exp)
    for ug in user_group_list:
        session.refresh(ug)

    return expenses_list


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


def test_create_expense_with_splits(
    client, session: Session, users: List[User], groups: List[Group]
):
    user = users[0]
    group = groups[0]
    payload = {
        "title": "Lunch",
        "amount": 100,
        "group_id": group.id,
        "user_id": user.id,
        "splits": [
            {
                "user_id": user.id,  # This is id of each in the group
                "group_id": group.id,  # TODO: This is redundant. Remove it from model
                "amount": 30,
            },
            {
                "user_id": user.id,  # This is id of each in the group
                "group_id": group.id,
                "amount": 70,
            },
        ],
    }

    response = client.post("/expenses", json=payload)
    assert response.status_code == 200

    data = response.json()

    assert "splits" in data
    assert len(data["splits"]) == 2

    db_expense = session.exec(select(Expense)).all()
    db_splits = session.exec(select(Split)).all()

    assert len(db_expense) == 1
    assert len(db_splits) == 2

    assert db_expense[0].title == payload["title"]
    assert db_expense[0].amount == payload["amount"]
    assert db_expense[0].group_id == payload["group_id"]
    assert db_expense[0].user_id == payload["user_id"]

    assert db_splits[0].user_id == payload["user_id"]
    assert db_splits[0].amount == payload["splits"][0]["amount"]
    assert db_splits[1].user_id == payload["user_id"]
    assert db_splits[1].amount == payload["splits"][1]["amount"]


def test_cascade_splits_delete(expenses, session: Session):
    """Deleting expense should automatically delete all the splits"""
    expense = expenses[0]
    db_splits_pre_delete = session.exec(
        select(Split).where(Split.expense_id == expense.id)
    ).all()
    assert len(db_splits_pre_delete) == 2

    # Perfrom a delete on expense and check if its expenses are deleted
    session.delete(expense)
    session.commit()
    # session.refresh(expense) # This does work after the obj is deleted from session. Throws Error
    db_splits_post_delete = session.exec(
        select(Split).where(Split.expense_id == expense.id)
    ).all()
    assert len(db_splits_post_delete) == 0
