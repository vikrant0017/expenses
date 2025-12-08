from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app import models
from app.crud.expense import create_expense, get_expenses
from app.database import get_session
from app.deps import get_current_user
from app.models import UserGroup

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=models.ExpenseRead)
def create_expenses(
    expense: models.ExpenseCreate,
    user_id: Annotated[int, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    # Will automatically handle inserting splits into Splits table since we have defined in the Relationship
    # to backpopulate Expense.splits with Splits.expense
    db_expense = create_expense(session, user_id, expense)
    return db_expense


@router.get("", response_model=List[models.ExpenseRead])
def read_expenses(
    user_id: Annotated[int, Depends(get_current_user)],
    group_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
):
    """
    Read expenses for a certain user - all user's expense or all expenses in a group the user is part of
    user_id is mandatory even from groups to only allowing reading expenses of a group that user is part of
    """

    # Verify if the user and group are associated before returning expenses
    if group_id:
        user_group = session.exec(
            select(UserGroup).where(
                UserGroup.user_id == user_id, UserGroup.group_id == group_id
            )
        ).all()

        if not len(user_group):
            raise HTTPException(
                404, "No association exists between the provided user_id and  group_id"
            )

    expenses = get_expenses(session, user_id, group_id, skip, limit)

    return expenses
