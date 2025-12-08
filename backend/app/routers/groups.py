from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app import models
from app.crud.groups import create_group, get_user_groups
from app.database import get_session
from app.deps import get_current_user

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=models.GroupRead)
def create_groups(
    group: models.GroupCreate,
    user_id: Annotated[int, Depends(get_current_user)],
    session: Session = Depends(get_session),
):
    """Create a new group associated with the user"""

    created_group = create_group(session, user_id, group)
    return created_group


@router.get("", response_model=List[models.GroupRead])
def read_groups(
    user_id: Annotated[int, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
):
    """Get all the groups of a user"""
    return get_user_groups(session, user_id, skip, limit)
