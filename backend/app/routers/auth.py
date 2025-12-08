from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select
from starlette.status import HTTP_401_UNAUTHORIZED

from app.database import get_session
from app.models import User, UserCreate
from app.utils import hash_password, jwt_encode, verify_password

router = APIRouter(tags=["auth"])


@router.post("/token")  # OAspec
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session),
):
    username = form_data.username
    password = form_data.password

    try:
        db_user = session.exec(select(User).where(User.username == username)).one()
    except NoResultFound:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Unauthorized user",
            headers={"WWW-Authenticate": "Bearer"},  # OAuth Spec
        )

    if not verify_password(password, db_user.password):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Unauthorized user",
            headers={"WWW-Authenticate": "Bearer"},  # OAuth Spec
        )

    token = jwt_encode({"user_id": db_user.id})

    # Oauth reponse spec: https://www.oauth.com/oauth2-servers/access-tokens/access-token-response/
    return {"user_id": db_user.id, "access_token": token, "token_type": "bearer"}


@router.post("/signup")
def signup(user: UserCreate, session: Session = Depends(get_session)):
    db_user = User.model_validate(user)
    db_user.password = hash_password(user.password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    token = jwt_encode({"user_id": db_user.id})

    return {"user_id": db_user.id, "access_token": token, "token_type": "bearer"}
