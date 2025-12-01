from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app import models
from app.database import get_session

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=models.GroupRead)
def create_groups(group: models.GroupCreate, session: Session = Depends(get_session)):
    """
    Note: Groups can't be created in isolation - it must be associated with the user who requested
    for the group creation - the admin
    """
    # Skipping user_id verification not required as it will be performed as part of auth later
    db_group = models.Group.model_validate(group)

    session.add(db_group)
    session.flush()  # We dont want to commit now since this will commit the transaction
    session.refresh(db_group)

    user_group = models.UserGroup(user_id=group.user_id, group_id=db_group.id)
    session.add(user_group)
    session.commit()

    return db_group


@router.get("", response_model=List[models.UserRead])
def read_groups(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
):
    """Fetch all the groups of the users"""
    users = session.exec(
        select(models.Group)
        .join(models.UserGroup)
        .where(models.UserGroup.user_id == user_id)
        .offset(skip)
        .limit(limit)
    ).all()
    return users
