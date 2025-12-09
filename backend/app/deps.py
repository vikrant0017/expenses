from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from app.database import get_session
from app.models import UserGroup
from app.utils import jwt_decode

# extracts the scheme and token
oauth2scheme = OAuth2PasswordBearer(tokenUrl="token")  # tokenUrl - For the OpenAPI docs


def get_current_user(token: Annotated[str, Depends(oauth2scheme)]) -> int:
    # The token is some secret we need to decode and get the user
    json = jwt_decode(token)

    if not json.get("user_id"):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Unauthorized user",
            headers={"WWW-Authenticate": "Bearer"},  # OAuth Spec
        )

    return json.get("user_id")


def require_group_membership(
    group_id: int,
    user_id: Annotated[int, Depends(get_current_user)],
    session: Session = Depends(get_session),
) -> None:
    """Verify if user is part of the group to perform group operations"""
    try:
        session.exec(
            select(UserGroup.user_id).where(
                UserGroup.user_id == user_id, UserGroup.group_id == group_id
            )
        ).one()
    except NoResultFound:
        raise HTTPException(HTTP_403_FORBIDDEN, "User is not a member of the group")
