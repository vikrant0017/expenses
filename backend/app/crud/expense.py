from sqlmodel import Session, select

from app.models import Expense, ExpenseCreate, Split


def create_expense(session: Session, user_id: int, expense: ExpenseCreate):
    """
    Create a new group and associate it with a user.

    Args:
        session (Session): Database session for performing operations.
        user_id (int): ID of the user creating and being associated with the group.
        group (GroupCreate): Group data for creating the new group.

    Returns:
        Group: The newly created group object with its database ID.
    """
    expense_data = expense.model_dump()
    expense_data["user_id"] = user_id

    user_expense = Expense.model_validate(expense_data)
    if expense_data["splits"] and len(expense_data["splits"]):
        for s in expense_data["splits"]:
            ss = Split(**s, group_id=expense.group_id)
            user_expense.splits.append(ss)

    session.add(user_expense)
    session.commit()

    return user_expense


def get_expenses(
    session: Session,
    user_id: int,
    group_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
):
    """Get all expenses of a user. If group_id is provided get only the expenses
    in from that group"""
    if group_id is None:
        stmt = select(Expense).where(Expense.user_id == user_id)
    else:
        stmt = select(Expense).where(
            Expense.user_id == user_id, Expense.group_id == group_id
        )

    stmt = stmt.offset(skip).limit(limit)
    expenses = session.exec(stmt).all()

    return expenses
