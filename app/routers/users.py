from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

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


@router.get("", response_model=List[models.UserRead])
def read_users(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    users = session.exec(select(models.User).offset(skip).limit(limit)).all()
    return users
