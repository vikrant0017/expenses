from typing import Sequence

from sqlmodel import Session, select

from app.models import (
    Group,
    GroupCreate,
    MemberCreate,
    MemberRead,
    User,
    UserGroup,
    UserRead,
)


def create_group(session: Session, user_id: int, group: GroupCreate):
    """
    Create a new group and associate it with a user.

    Args:
        session (Session): Database session for performing operations.
        user_id (int): ID of the user creating and being associated with the group.
        group (GroupCreate): Group data for creating the new group.

    Returns:
        Group: The newly created group object with its database ID.
    """
    # Skipping user_id verification not required as it will be performed as part of auth later
    db_group = Group.model_validate(group)

    session.add(db_group)
    # Flush to get the group id to add to associate user and gropup in join table
    session.flush()
    session.refresh(db_group)

    user_group = UserGroup(user_id=user_id, group_id=db_group.id)
    session.add(user_group)
    session.commit()

    return db_group


def get_user_groups(session: Session, user_id: int, skip: int, limit: int):
    """Get all the groups that the user is member of"""
    users = session.exec(
        select(Group)
        .join(UserGroup)
        .where(UserGroup.user_id == user_id)
        .offset(skip)
        .limit(limit)
    ).all()

    return users


def add_user(session: Session, group_id, user_id):
    """Add user to a group"""
    # Skipping user_id verification not required as it will be performed as part of auth later
    user_group = UserGroup(user_id=user_id, group_id=group_id)
    session.add(user_group)
    session.commit()
    session.refresh(user_group)
    return user_group


def create_member(session: Session, member: MemberCreate):
    """Add member(user) to a group"""
    # Skipping user_id verification not required as it will be performed as part of auth later
    user_group = UserGroup(user_id=member.id, group_id=member.group_id)
    session.add(user_group)
    session.commit()
    session.refresh(user_group)
    return user_group


def read_members(session: Session, member: MemberRead) -> Sequence[UserRead]:
    """Get member(user) to a group"""
    # Verify if user is part of the group before reading the members
    members = session.exec(
        select(User.id, User.username, User.name)
        .join(UserGroup)
        .where(UserGroup.group_id == member.group_id)
    ).all()
    return [UserRead.model_validate(user) for user in members]
