from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from starlette.status import HTTP_404_NOT_FOUND

from app import models
from app.database import get_session

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=models.UserRead)
def create_user(user: models.UserCreate, session: Session = Depends(get_session)):
    db_user = models.User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/{user_id}", response_model=models.UserRead)
def read_user(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
):
    users = session.exec(
        select(models.User).where(models.User.id == user_id).offset(skip).limit(limit)
    ).all()

    if len(users) == 0:
        raise HTTPException(HTTP_404_NOT_FOUND, "User not found")

    return users[0]  # select returns an array even for single row
