import json
from decimal import Decimal

import pytest
from assertpy import assert_that
from faker import Faker
from fastapi.testclient import TestClient

from app import models
from app.crud.expense import create_expense
from app.crud.groups import add_user, create_group
from app.crud.users import create_user
from app.database import get_session
from app.deps import get_current_user
from app.main import app
from app.models import (
    Expense,
    GroupCreate,
    UserCreate,
)


@pytest.fixture
def user_factory(request):
    """Factory fixture that creates a new user on each call"""

    def _create_user(username: str | None = None, password: str | None = None):
        faker = Faker()
        session = request.getfixturevalue("session")
        user = UserCreate(
            username=username or faker.user_name(),
            password=password or faker.password(8),
        )
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
        faker = Faker()
        session = request.getfixturevalue("session")

        group = GroupCreate(name=group_name or faker.color_name())
        db_group = create_group(session, user_id, group)

        return db_group

    return _create_user_with_group


@pytest.fixture
def user_group_factory(request):
    """Factory fixture that creates a new user and authenticated client on each call"""

    def _add_user_to_group(user_id: int, group_id: int):
        session = request.getfixturevalue("session")

        return add_user(session, group_id, user_id)

    return _add_user_to_group


@pytest.fixture()
def expenses_factory(
    request, user_factory, group_factory, user_group_factory, split_users=None
):
    def _create_expense(user_id, group_id):
        session = request.getfixturevalue("session")

        # Add user to the group for splits
        # split_user = user_factory("User2", "pass2")
        # group = group_factory(split_user.id, "Group1")
        # user_group = user_group_factory(user.id, group_id)

        faker = Faker()

        # Generate fake title and total amount (keep group_id and user_id from parameters)
        title = faker.sentence(nb_words=3)
        total_amount = Decimal(
            str(
                faker.pyfloat(
                    left_digits=3,
                    right_digits=2,
                    positive=True,
                    min_value=10,
                    max_value=200,
                )
            )
        )

        # Create two split amounts that sum to the total_amount
        # percent = faker.random_int(min=20, max=80)

        # first_amount = (total_amount * Decimal(percent) / Decimal(100)).quantize(
        #     Decimal("0.01")
        # )
        # second_amount = (total_amount - first_amount).quantize(Decimal("0.01"))

        expense = models.ExpenseCreate(
            title=title,
            amount=total_amount,
            group_id=group_id,
            # splits=[
            #     SplitCreate(  # pyright: ignore[reportCallIssue]
            #         user_id=user
            #         amount=first_amount,
            #     ),
            #     SplitCreate(  # pyright: ignore[reportCallIssue]
            #         amount=second_amount,
            #     ),
            # ],
        )

        db_expense = create_expense(session, user_id, expense)
        return db_expense

    return _create_expense


def compare_expenses(expenses: list[Expense], data: list[dict]):
    # To make sure the custom added passes through JSON serialization
    for d, e in zip(
        [{k: v for k, v in d.items() if k != "splits"} for d in data],
        [json.loads(exp.model_dump_json()) for exp in expenses],
    ):
        assert d == e


def test_create_expense(auth_client_factory, user_factory, group_factory):
    user = user_factory()
    group = group_factory(user.id)

    client_with_auth = auth_client_factory(user.id)

    # TODO: Create a faker helper to create a payload
    payload = {
        "title": "Lunch",
        "amount": "50.45",
        "group_id": group.id,
    }

    response = client_with_auth.post("/expenses", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert payload.items() <= data.items()


def test_read_user_expenses(
    auth_client_factory, user_factory, group_factory, expenses_factory
):
    """It should return all the expenses created by the user"""

    user = user_factory()
    group = group_factory(user.id)

    expenses: list[Expense] = [expenses_factory(user.id, group.id) for _ in range(2)]

    client_with_auth = auth_client_factory(user.id)
    res = client_with_auth.get("/expenses")
    assert res.status_code == 200

    data = res.json()

    compare_expenses(expenses, data)


def test_user_can_only_read_own_expenses(
    auth_client_factory,
    user_factory,
    user_group_factory,
    group_factory,
    expenses_factory,
):
    user1 = user_factory()
    user2 = user_factory()
    group = group_factory(user1.id)
    user_group_factory(user2.id, group.id)

    user1_expenses = [expenses_factory(user1.id, group.id) for _ in range(2)]
    user2_expenses = [expenses_factory(user2.id, group.id) for _ in range(2)]

    # -- User 1 -- #
    client_with_auth = auth_client_factory(user1.id)
    res = client_with_auth.get("/expenses")
    assert res.status_code == 200
    data = res.json()
    compare_expenses(user1_expenses, data)

    # -- User 2 -- #
    client_with_auth = auth_client_factory(user2.id)
    res = client_with_auth.get("/expenses")
    assert res.status_code == 200
    data = res.json()
    compare_expenses(user2_expenses, data)


def test_user_group_expenses(
    auth_client_factory,
    user_factory,
    group_factory,
    expenses_factory,
):
    user = user_factory()
    group1 = group_factory(user.id)
    group2 = group_factory(user.id)

    group1_expenses = [expenses_factory(user.id, group1.id) for _ in range(2)]
    group2_expenses = [expenses_factory(user.id, group2.id) for _ in range(2)]

    client_with_auth = auth_client_factory(user.id)

    # -- Group 1 Expenses -- #
    res = client_with_auth.get(f"/expenses?group_id={group1.id}")
    data = res.json()
    assert res.status_code == 200
    compare_expenses(group1_expenses, data)

    # -- Group 2 Expenses -- #
    res = client_with_auth.get(f"/expenses?group_id={group2.id}")
    assert res.status_code == 200
    data = res.json()
    compare_expenses(group2_expenses, data)


def test_fail_user_group(user_factory, group_factory, auth_client_factory):
    """
    It should return a 404 error if user is not part of the group
    """

    user1 = user_factory()
    user2 = user_factory()
    group1 = group_factory(user1.id)
    group2 = group_factory(user2.id)

    client_with_auth = auth_client_factory(user1.id)
    res = client_with_auth.get(f"/expenses?group_id={group2.id}")
    assert res.status_code == 404

    client_with_auth = auth_client_factory(user2.id)
    res = client_with_auth.get(f"/expenses?group_id={group1.id}")
    assert res.status_code == 404


def test_create_expense_with_splits(
    auth_client_factory, user_factory, group_factory, user_group_factory
):
    user1 = user_factory()
    user2 = user_factory()
    group = group_factory(user1.id)
    user_group_factory(user2.id, group.id)

    client_with_auth = auth_client_factory(user1.id)

    # TODO: Create a faker helper to create a payload
    payload = {
        "title": "Lunch",
        "amount": "100",
        "group_id": group.id,
        "splits": [
            {
                "user_id": user1.id,  # This is id of each in the group
                "amount": "30",
            },
            {
                "user_id": user2.id,  # This is id of each in the group
                "amount": "70",
            },
        ],
    }

    response = client_with_auth.post("/expenses", json=payload)
    data = response.json()

    assert response.status_code == 200

    payload_splits = payload.pop("splits")
    data_splits = data.pop("splits")
    # assert payload <= data

    assert_that(payload).is_subset_of(data)
    for ps, ds in zip(payload_splits, data_splits):
        assert_that(ps).is_subset_of(ds)
