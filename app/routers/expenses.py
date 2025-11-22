from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=schemas.ExpenseRead)
async def create_expense(
    expense: schemas.ExpenseCreate, db: AsyncSession = Depends(get_db)
):
    # Verify group and user exist (optional but good practice)
    # For simplicity, we assume they exist or let DB constraints handle it (will raise IntegrityError)

    db_expense = models.Expense(
        title=expense.title,
        description=expense.description,
        amount=expense.amount,
        group_id=expense.group_id,
        user_id=expense.user_id,
        timestamp=datetime.utcnow(),  # In real app, might come from request
    )
    db.add(db_expense)
    await db.commit()
    await db.refresh(db_expense)
    return db_expense


@router.get("", response_model=List[schemas.ExpenseRead])
async def read_expenses(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Expense).offset(skip).limit(limit))
    expenses = result.scalars().all()
    return expenses
