from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app import models
from app.database import get_session
from app.models import Expense, Group, User, UserGroup

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=models.ExpenseRead)
def create_expense(
    expense: models.ExpenseCreate, session: Session = Depends(get_session)
):
    db_expense = models.Expense.model_validate(expense)
    session.add(db_expense)
    session.commit()
    session.refresh(db_expense)
    return db_expense


@router.get("", response_model=List[models.ExpenseRead])
def read_expenses(
    user_id: int,  # User is required to prevent from acessing other groups
    group_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
):
    """
    Read expenses for a certain user - all user's expense or all expenses in a group the user is part of
    user_id is mandatory even from groups to only allowing reading expenses of a group that user is part of
    """

    if group_id:
        # Verify if the user and group are associated before returning expenses
        user_group = session.exec(
            select(UserGroup).where(
                UserGroup.user_id == user_id, UserGroup.group_id == group_id
            )
        ).all()

        if not len(user_group):
            raise HTTPException(
                404, "No association exists between the provided user_id and  group_id"
            )

        expenses = session.exec(
            select(Expense)
            .where(Expense.user_id == user_id, Expense.group_id == group_id)
            .offset(skip)
            .limit(limit)
        ).all()

        return expenses
    else:
        expenses = session.exec(
            select(Expense).where(Expense.user_id == user_id).offset(skip).limit(limit)
        ).all()

        return expenses
