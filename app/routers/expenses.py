from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app import models
from app.database import get_session

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=models.ExpenseRead)
def create_expense(
    expense: models.ExpenseCreate, session: Session = Depends(get_session)
):
    # Verify group and user exist (optional but good practice)
    # For simplicity, we assume they exist or let DB constraints handle it (will raise IntegrityError)

    db_expense = models.Expense.model_validate(expense)
    # Override timestamp if needed, or let default handle it. 
    # The original code set timestamp=datetime.utcnow(), but model has default_factory.
    # However, ExpenseCreate doesn't have timestamp, so it will use default.
    
    session.add(db_expense)
    session.commit()
    session.refresh(db_expense)
    return db_expense


@router.get("", response_model=List[models.ExpenseRead])
def read_expenses(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    expenses = session.exec(select(models.Expense).offset(skip).limit(limit)).all()
    return expenses
