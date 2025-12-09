from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app import models
from app.crud.groups import create_group, create_member, get_user_groups, read_members
from app.database import get_session
from app.deps import get_current_user, require_group_membership

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


@router.post("/{group_id}/members", response_model=models.UserGroup)
def post_members(
    group_id: int,
    member: models.MemberCreateRequest,
    user_id: Annotated[int, Depends(get_current_user)],
    session: Session = Depends(get_session),
    _: None = Depends(require_group_membership),
):
    created_member = create_member(
        session=session,
        member=models.MemberCreate(group_id=group_id, id=member.id),
    )
    return created_member


@router.get("/{group_id}/members", response_model=list[models.UserRead])
def get_members(
    group_id: int,
    user_id: Annotated[int, Depends(get_current_user)],
    session: Session = Depends(get_session),
    _: None = Depends(require_group_membership),
):
    group_members = read_members(
        session, models.MemberRead(id=user_id, group_id=group_id)
    )
    return group_members
